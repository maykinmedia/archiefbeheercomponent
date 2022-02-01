import React from 'react';
import ReactDOM from 'react-dom';

import ListZaken from './ListZaken';
import {jsonScriptToVar} from '../../utils';
import { UrlsContext } from '../context';
import ErrorBoundary from '../ErrorBoundary';



const mount = () => {
    const node = document.getElementById('react-zaken-without-archive-date');
    if (!node) return;

    const { zakenUrl, archiveUpdateUrl, exportZakenUrl } = node.dataset;
    const zaaktypeChoices = jsonScriptToVar('zaaktype-choices');

    ReactDOM.render(
        <UrlsContext.Provider value={{archiveUpdateUrl: archiveUpdateUrl, exportZakenUrl:exportZakenUrl}}>
            <ErrorBoundary>
                <ListZaken
                    zakenUrl={zakenUrl}
                    zaaktypen={zaaktypeChoices}
                />
            </ErrorBoundary>
        </UrlsContext.Provider>,
        node
    );
};


mount();
