import React from 'react';
import ReactDOM from 'react-dom';

import ListZaken from './ListZaken';
import {jsonScriptToVar} from '../../utils';
import { ArchiveUpdateUrlContext } from '../context';



const mount = () => {
    const node = document.getElementById('react-zaken-without-archive-date');
    if (!node) return;

    const { zakenUrl, archiveUpdateUrl } = node.dataset;
    const zaaktypeChoices = jsonScriptToVar('zaaktype-choices');

    ReactDOM.render(
        <ArchiveUpdateUrlContext.Provider value={archiveUpdateUrl}>
            <ListZaken
                zakenUrl={zakenUrl}
                zaaktypeChoices={zaaktypeChoices}
            />
        </ArchiveUpdateUrlContext.Provider>,
        node
    );
};


mount();
