import React from "react";
import ReactDOM from "react-dom";
import { jsonScriptToVar } from '../../utils';
import {DestructionForm} from "./destruction-form";


const mount = () => {
    const node = document.getElementById('react-destruction-list');
    if (!node) return;

    const zaaktypen = jsonScriptToVar('zaaktype-choices');
    const { zakenUrl, url, csrftoken } = node.dataset;

    ReactDOM.render(
        <DestructionForm
            zaaktypen={zaaktypen}
            zakenUrl={zakenUrl}
            url={url}
            csrftoken={csrftoken}
        />,
        node
    );
};


mount();
