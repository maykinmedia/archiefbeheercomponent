import React from 'react';
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

export default BronorganisatieSelect;
