import React from "react";
import ReactDOM from "react-dom";
import Modal from "react-modal";

import { jsonScriptToVar } from '../../utils';
import { ListItemFormset } from "./list-item-formset";
import { FormsetConfigContext } from "./context";


const mount = () => {
    const node = document.getElementById('react-destruction-list-detail');
    if (!node) return;

    const {itemsUrl} = node.dataset;
    const formsetConfig = jsonScriptToVar('formset-config');

    Modal.setAppElement('#react-destruction-list-detail');

    ReactDOM.render(
        <FormsetConfigContext.Provider value={formsetConfig}>
            <ListItemFormset
                itemsUrl={itemsUrl}
            />
        </FormsetConfigContext.Provider>,
        node
    )
};


mount();
