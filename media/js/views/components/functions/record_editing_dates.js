define(['jquery',
    'knockout',
    'viewmodels/function',
    'bindings/chosen', 'arches'],
function($, ko, FunctionViewModel, chosen, arches) {
    return ko.components.register('views/components/functions/record_editing_dates', {
        viewModel: function(params) {
            FunctionViewModel.apply(this, arguments);
            let self = this
            //Params ---
            this.triggering_nodegroups = params.config.triggering_nodegroups;

            //TODO: Update UUID's to match live server
            this.triggering_nodegroups(['e420a6e6-8ff9-11ec-bbf3-00155d9326d1','ffbcc420-8ff9-11ec-9340-00155d9326d1'])
        }
        ,
        template: {
            require: 'text!templates/views/components/functions/record_editing_dates.htm'

        }
    });
});