import React from 'react';
import PropTypes from 'prop-types';

import {countObjectKeys, getObjectKeys} from '../../utils';


const ExportButton = ({exportZakenUrl, checkboxes}) => {
    const countSelectedCheckboxes = countObjectKeys(checkboxes);

    const getExportUrl = () => {
      let exportUrl = new URL(window.location.href);
      exportUrl.pathname = exportZakenUrl;
      exportUrl.searchParams.set('zaken_urls', getObjectKeys(checkboxes));
      return exportUrl.href;
    };

    return (
        <>
            <a
                href={countSelectedCheckboxes ? getExportUrl() : '#'}
                type="button"
                className={`btn ${countSelectedCheckboxes ? '' : 'btn--disabled'}`}
                title="Exporteer de geselecteerde zaken als een Excel spreadsheet."
            >Exporteren</a>
            <div>{countSelectedCheckboxes} zaken geselecteerd</div>
        </>
    );
};


ExportButton.propTypes = {
    exportZakenUrl: PropTypes.string.isRequired,
    checkboxes: PropTypes.object.isRequired,
};


export default ExportButton;
