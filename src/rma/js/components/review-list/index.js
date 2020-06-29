import React from "react";
import ReactDOM from "react-dom";
import Modal from "react-modal";

import { ConstantsContext } from "./context";
import { ReviewItemFormset } from "./review-item-formset";


const mount = () => {
    const node = document.getElementById('react-review-items');
    if (!node) return;

    const { itemsUrl, zaakDetailUrl } = node.dataset;

    // constants
    const prefix = "item_reviews";
    const constants = { prefix, zaakDetailUrl };

    Modal.setAppElement('#react-review-items');

    ReactDOM.render(
        <ConstantsContext.Provider value={constants}>
            <ReviewItemFormset
                itemsUrl={itemsUrl}
                zaakDetailUrl={zaakDetailUrl}
            />
        </ConstantsContext.Provider>,
        node
    );
};


mount();
