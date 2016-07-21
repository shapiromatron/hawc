/*

Test crosswalk:

Failure bin:
 - 0: no-bin change
 - 1: warning
 - 2: failure

Each test should return nothing or {
    bin: <Failure bin Integer[0 - 2]>,
    notes: <String>
}

*/

let fieldExists=function(output, key, failure_bin){

    },
    testCrosswalk = {
        'BMD'(logic, model){
        },
        'BMDL'(logic, model){
        },
        'BMDU'(logic, model){
        },
        'AIC'(logic, model){
        },
        'Variance Type'(logic, model){
        },
        'Variance Fit'(logic, model){
        },
        'GGOF'(logic, model){
        },
        'GGOF (Cancer)'(logic, model){
        },
        'BMD/BMDL (serious)'(logic, model){
        },
        'BMD/BMDL (warning)'(logic, model){
        },
        'Residual of Interest'(logic, model){
        },
        'Warnings'(logic, model){
        },
        'BMD higher'(logic, model){
        },
        'BMDL higher'(logic, model){
        },
        'Low BMD (warning)'(logic, model){
        },
        'Low BMDL (warning)'(logic, model){
        },
        'Low BMD (serious)'(logic, model){
        },
        'Low BMDL (serious)'(logic, model){
        },
        'Control residual'(logic, model){
        },
        'Control stdev'(logic, model){
        },
    };




let apply_logic = function(logics, models, endpoint){
    console.log(logics, models, endpoint);
    // get function associated with each test.
    // logics.filter((d)=>{
    //     // filter by data-type
    //     switch(endpoint){
    //     case 'C':
    //         return d.continuous_on;
    //     case 'D':
    //         return d.dichotomous_on;
    //     case 'DC':
    //         return d.cancer_dichotomous_on;
    //     default:
    //         throw('Unknown data type')
    //     }
    // }).each((d)=>{
    //     d.func = testCrosswalk[d.name];
    // });

    // // apply unit-tests to each model
    // models.forEach((model)=> {

    //     // set global recommendations
    //     model.recommended = false;
    //     model.recommended_text = '';

    //     // set no warnings by default
    //     model.logic_bin = 0;  // set innocent until proven guilty
    //     model.logic_notes = {
    //         0: [],
    //         1: [],
    //         2: [],
    //     };

    //     // apply tests for each model
    //     logics.forEach((logic)=> {
    //         let x = logic.func(logic, model);
    //         if (x.bin){
    //             model.logic_bin = Math.max(x.bin, model.logic_bin);
    //         }
    //         if (x.notes){
    //             model.logic_notes[x.bin].push(x.notes);
    //         }
    //     });
    // });

    // apply model recommendations, filter by bmr
};

export {apply_logic};
