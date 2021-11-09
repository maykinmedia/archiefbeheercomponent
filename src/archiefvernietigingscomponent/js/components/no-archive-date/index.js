import React from 'react';
import ReactDOM from 'react-dom';

import ListZaken from './ListZaken';



const mount = () => {
    const node = document.getElementById('react-zaken-without-archive-date');
    if (!node) return;

    const { zakenUrl } = node.dataset;

    ReactDOM.render(
        <ListZaken
            zakenUrl={zakenUrl}
        />,
        node
    );
};


mount();
