import React from 'react';
import PropTypes from 'prop-types';

import {CheckboxInput} from '../../forms/inputs';


const ZaakIdentificatieFilter = ({zakenIdentificaties, selected, onChange}) => {
    const checkboxes = zakenIdentificaties.map((zaak, index) => {
        return (
            <label key={index}>
                <CheckboxInput
                    checked={selected.includes(zaak)}
                    name={zaak}
                    onChange={(event) => {
                        if (event.target.checked){
                            onChange([...selected, zaak]);
                        } else {
                            onChange(selected.filter((value) => {
                                return value !== zaak;
                            }));
                        }
                    }}
                />
                {zaak}
            </label>
        )
    });

    return (
        <>{checkboxes}</>
    );
};


ZaakIdentificatieFilter.propTypes = {
    zakenIdentificaties: PropTypes.arrayOf(PropTypes.string),
    selected: PropTypes.arrayOf(PropTypes.string),
    onChange: PropTypes.func
};


export default ZaakIdentificatieFilter;
