define(['knockout',
    'viewmodels/function',
    'viewmodels/concept-select',
    'bindings/select2-query',
    'views/components/widgets/concept-multiselect',
    'views/components/simple-switch'],
    function (ko, FunctionViewModel, ConceptSelectViewModel, select2Query) {
        //Classes
        class Rule {
            constructor(selectedNodeGroup, selectedNode, selectedVal, userGroups) {
                this.selectedNodeGroup = selectedNodeGroup
                this.selectedNode = selectedNode
                this.selectedVal = selectedVal
                this.userGroups = userGroups
            }
        }

        //Methods
        const ruleExists = function(existingRules, newRule){
            existingRules().forEach(rule => {

                // if (ko.mapping.toJS(rule.selectedNodeGroup) == ko.mapping.toJS(newRule.selectedNodeGroup)
                // && ko.mapping.toJS(rule.selectedNode) == ko.mapping.toJS(newRule.selectedNode)
                // && ko.mapping.toJS(rules.selectedVal) == ko.mapping.toJS(newRule.selectedVal)
                // && testUserGroup(ko.mapping.toJS(rule.userGroups)) == testUserGroup(ko.mapping.toJS(newRule.userGroups)))
                console.log(ko.mapping.toJS(rule))
                
                if (JSON.stringify(ko.mapping.toJS(rule)) == JSON.stringify(newRule))
                return true
            });
            console.log(ko.mapping.toJS(newRule))
            return false
        }

        // const testUserGroup = function(existingUserGroup, newUserGroup){
        //     let isTrue
        //     newUserGroup.forEach(newUser => {
        //         existingUserGroup.forEach(user => {
        //             if(newUser.name == user.name && newUser.selectedVal == user.selectedVal) isTrue = true
        //             else return isTrue = false
        //         })
        //     })
        //     return isTrue
        // }

        return ko.components.register('views/components/functions/eamena-permissions', {
            viewModel: function (params) {
                FunctionViewModel.apply(this, arguments);
                var self = this;
                var nodegroups = {};
                this.rerender = ko.observable(true);
                this.cards = ko.observableArray();
                this.nodes = ko.observableArray([]);
                this.concepts = ko.observableArray([]);
                this.concept_nodes = ko.observableArray();
                this.concept_node = ko.observable();
                this.initialUsers = ko.observableArray();
                this.triggering_nodegroups = params.config.triggering_nodegroups;

                ConceptSelectViewModel.apply(this, [params]);

                this.rules = params.config.rules

                //new rule
                let newRule
                //Blank Rules
                this.selectedNodeGroup = ko.observable()
                this.selectedNode = ko.observable()
                this.selectedVal = ko.observable()
                this.userGroups = ko.observableArray()

                // Use the custom /get/users endpoint to get up to date list of users. ** must add the endpoint
                $.getJSON("http://127.0.0.1:8000/get/users", function (data) {
                    self.initialUsers(data)
                }); //Complete

                // Requires push method when we get to multiple rules 
                this.selectedNodeGroup.subscribe(function (val) {
                    self.triggering_nodegroups([val]);
                });
                
                // Generates the list of nodegroups/cards to be used in the drop down        
                this.graph.cards.forEach(function (card) {
                    var found = !!_.find(this.graph.nodegroups, function (nodegroup) {
                        return nodegroup.parentnodegroup_id === card.nodegroup_id
                    }, this);
                    if (!found && !(card.nodegroup_id in nodegroups)) {
                        card.id = card.nodegroup_id;
                        card.text = card.name; // Card Names
                        this.cards.push(card); // Add to cards array
                        nodegroups[card.nodegroup_id] = true;
                    }

                }, this); //NOTE: Might not be complete

                // This generates the list of nodes once nodegroup is selected
                this.selectedNodeGroup.subscribe(function () {
                    self.rerender(false); //Toggling rerender forces the node options to load in the select2 dropdown when the card changes
                    var nodes = self.graph.nodes.filter(function (node) {
                        return node.nodegroup_id === self.selectedNodeGroup();
                    }).map(function (node) {
                        node.id = node.nodeid;
                        node.text = node.name;
                        return node;
                    });
                    // re-write nodes to only concept type nodes
                    var nodes = nodes.filter(function (node) {
                        return node.datatype === 'concept';
                    })
                    self.nodes.removeAll();
                    self.nodes(nodes);
                    self.rerender(true);
                    self.nodes().forEach(function (node) {

                    })

                });//Complete
                
                // Compare initialUsers to userGroups 
                // If they are identical, do nothing.
                // If there is a group in initialUsers but not in UserGroups, ADD 
                // If there is a group in userGroups but not in initialUsers, DELETE

                // This compares userGroups to initialUsers and if one is missing, add it.
                this.initialUsers.subscribe(function (val) {
                    val.forEach(function (v, i) {
                        if (self.userGroups().some((identity) => ko.unwrap(identity['identityName']) === v.name) === false) {
                            console.log("adding", v.name)
                            var groupEntry = {
                                identityName: ko.unwrap(v.name),
                                identityId: ko.unwrap(v.id),
                                identityType: ko.unwrap(v.type),
                                identityVal: ko.observable(true)
                            }
                            self.userGroups.push(groupEntry)
                        }
                    })
                }); //Complete

                // return concept list 
                this.selectedNode.subscribe(function (val) {
                    var concept_node = self.graph.nodes.find(function (node) {
                        return node.nodeid === val;
                    });
                    self.concept_node(concept_node);
                });//Complete


                this.userGroups.subscribe(val => console.log(ko.mapping.toJS(val)))

                this.selectedNodeGroup.valueHasMutated();// Forces the node value to load into the node options when the template is renderer
                // this.selectedVal.subscribe(a => {
                //     console.log("function arg", a)
                //     console.log("selected val", ko.mapping.toJS(this.selectedVal))
                //     //console.log("identity", ko.mapping.toJS(this.identityVal))
                //     console.log("in selected val" , a, ko.mapping.toJS(this.selectedVal))
                //     //create rule
                //    // newRule = new Rule(this.selectedNodeGroup, this.selectedNode, this.selectedVal, this.userGroups)
                // }) // keep this for validation later

                // //Create/Modify current rule when Identity vals change
                // if (this.identityVal) {
                //     console.log(this.identityVal)
                //     this.subscribe.identityVal(e => console.log("event", e))
                // }

                //methods
                this.addRule = function()
                {  
                    //console.log("rule", ko.mapping.toJS(this.selectedNodeGroup), ko.mapping.toJS(this.selectedNode), ko.mapping.toJS(this.selectedVal), ko.mapping.toJS(this.userGroups))
                    let newRule = new Rule(this.selectedNodeGroup,
                                                this.selectedNode,
                                                this.selectedVal,
                                                this.userGroups)
                    // console.log(ko.mapping.toJS(newRule))
                    // console.log(ruleExists(this.rules, newRule))
                    if(ruleExists(this.rules, newRule)) this.rules.push(newRule)
                    else alert("Rule already exists!")
                }
                    //TODO: Figure out why the function is alway false)
            },
            template: {
                require: 'text!templates/views/components/functions/eamena-permissions.htm'
            }

        });
    })
