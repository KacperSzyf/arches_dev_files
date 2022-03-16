define(['jquery',
    'knockout',
    'viewmodels/function',
    'bindings/chosen', 'arches'],
function($, ko, FunctionViewModel, chosen, arches) {
    return ko.components.register('views/components/functions/generate_node_value', {
        viewModel: function(params) {
            FunctionViewModel.apply(this, arguments);
            let self = this
            //Params ---
            this.triggering_nodegroups = params.config.triggering_nodegroups;
            this.keys = params.config.keys
            this.key_val = ko.observableArray()
            //end params
                                        //Community Value
            this.triggering_nodegroups(['7aaf957c-9f95-11ec-8951-00155d22601c'])

            //populate two arrays as a dictionary is not an observable 
            for(key in this.keys) this.key_val.push({"key":key, "value" :  ko.mapping.toJS(this.keys[key])})

        },
        template: {
            require: 'text!templates/views/components/functions/generate_node_value.htm'

        }
    });
});
