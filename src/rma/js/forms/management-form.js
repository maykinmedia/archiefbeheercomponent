import React from "react";


const ManagementForm = (props) => {
    const { prefix, initial_forms, total_forms, min_num_forms, max_num_forms } = props;
    return (
        <>
            <input type="hidden" name={`${prefix}-TOTAL_FORMS`} defaultValue={ total_forms } />
            <input type="hidden" name={`${prefix}-INITIAL_FORMS`} defaultValue={ initial_forms } />
            <input type="hidden" name={`${prefix}-MIN_NUM_FORMS`} defaultValue={ min_num_forms } />
            <input type="hidden" name={`${prefix}-MAX_NUM_FORMS`} defaultValue={ max_num_forms } />
        </>
    )
};


export { ManagementForm };
