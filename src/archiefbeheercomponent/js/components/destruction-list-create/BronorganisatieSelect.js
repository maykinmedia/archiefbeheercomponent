import React from 'react';
import PropTypes from 'prop-types';

import {CheckboxInput} from '../../forms/inputs';


const BronorganisatieSelect = ({bronorganisaties, selectedBronorganisaties, onChange}) => {

    const onChangeSelectedBronOrganisaties = (event, updatedBronorganisatie) => {
         const checked = event.target.checked;

         let updatedSelectedBronOrganisaties;

         if (checked){
                updatedSelectedBronOrganisaties = [...selectedBronorganisaties, updatedBronorganisatie];
            } else {
                updatedSelectedBronOrganisaties = [...selectedBronorganisaties].filter((value) => {
                    return value !== updatedBronorganisatie;
                });
            }

         onChange(updatedSelectedBronOrganisaties);
    };

    return (
        <>
            {
                bronorganisaties.map((bronorganisatie, index) => (
                    <label key={index}>
                        <CheckboxInput
                            checked={selectedBronorganisaties.includes(bronorganisatie)}
                            name={bronorganisatie}
                            onChange={(e) => onChangeSelectedBronOrganisaties(e, bronorganisatie)}
                        />
                        {bronorganisatie}
                    </label>
                ))
            }
        </>
    );
};


BronorganisatieSelect.propTypes = {
    bronorganisaties: PropTypes.arrayOf(PropTypes.string).isRequired,
    selectedBronorganisaties: PropTypes.arrayOf(PropTypes.string).isRequired,
    onChange: PropTypes.func.isRequired,
};


export default BronorganisatieSelect;
