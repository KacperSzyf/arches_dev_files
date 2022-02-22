define(['jquery',
    'knockout',
    'viewmodels/function',
    'bindings/chosen', 'arches'],
function($, ko, FunctionViewModel, chosen, arches) {
    return ko.components.register('views/components/functions/generate_location_qualifiers', {
        viewModel: function(params) {
            FunctionViewModel.apply(this, arguments);
            let self = this
            //Params ---
            this.triggering_nodegroups = params.config.triggering_nodegroups;
            //end params
            this.triggering_nodegroups(['e420a6e6-8ff9-11ec-bbf3-00155d9326d1'])
        }//5844718c-7dcc-11ec-a910-00155db3508e
        ,
        template: {
            require: 'text!templates/views/components/functions/generate_location_qualifiers.htm'

        }
    });
});