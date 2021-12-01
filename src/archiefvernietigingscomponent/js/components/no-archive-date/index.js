import React from 'react';
import ReactDOM from 'react-dom';

import ListZaken from './ListZaken';
import {jsonScriptToVar} from '../../utils';



const mount = () => {
    const node = document.getElementById('react-zaken-without-archive-date');
    if (!node) return;

    const { zakenUrl } = node.dataset;
    const zaaktypeChoices = jsonScriptToVar('zaaktype-choices');

    ReactDOM.render(
        <ListZaken
            zakenUrl={zakenUrl}
            zaaktypeChoices={zaaktypeChoices}
        />,
        node
    );
};


mount();
