import React from "react";
import ReactDOM from "react-dom";
import Modal from "react-modal";

import { jsonScriptToVar } from '../../utils';
import { ConstantsContext } from "./context";
import { ReviewForm } from "./review-form";


const mount = () => {
    const node = document.getElementById('react-review-create');
    if (!node) return;

    const { itemsUrl, zaakDetailUrl, zaakDetailPermission } = node.dataset;
    const destructionList = jsonScriptToVar('destruction-list');
    const formsetConfig = jsonScriptToVar('formset-config');

    // constants
    const constants = { formsetConfig, zaakDetailUrl, zaakDetailPermission };

    Modal.setAppElement('#react-review-create');

    ReactDOM.render(
        <ConstantsContext.Provider value={constants}>
            <ReviewForm
                itemsUrl={itemsUrl}
                destructionList={destructionList}
            />
        </ConstantsContext.Provider>,
        node
    );
};


mount();
