import React from "react";
import ReactDOM from "react-dom";
import Modal from "react-modal";

import { jsonScriptToVar } from '../../utils';
import { ConstantsContext } from "./context";
import { ReviewForm } from "./review-form";


const mount = () => {
    const node = document.getElementById('react-review-create');
    if (!node) return;

    const { itemsUrl, zaakDetailUrl, zaakDetailPermission, showOptionalColumns } = node.dataset;
    const destructionList = jsonScriptToVar('destruction-list');
    const formsetConfig = jsonScriptToVar('formset-config');
    const reviewComment = jsonScriptToVar('review-comment');

    // constants
    const constants = { formsetConfig, zaakDetailUrl, zaakDetailPermission, showOptionalColumns };

    Modal.setAppElement('#react-review-create');

    ReactDOM.render(
        <ConstantsContext.Provider value={constants}>
            <ReviewForm
                itemsUrl={itemsUrl}
                destructionList={destructionList}
                reviewComment={reviewComment}
            />
        </ConstantsContext.Provider>,
        node
    );
};


mount();
