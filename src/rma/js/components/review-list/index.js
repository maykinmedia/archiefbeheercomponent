import React from "react";
import ReactDOM from "react-dom";
import { ReviewItemFormset } from "./review-item-formset";


const mount = () => {
    const node = document.getElementById('react-review-items');
    if (!node) return;

    const { itemsUrl, csrftoken } = node.dataset;

    ReactDOM.render(
        <ReviewItemFormset
            itemsUrl={itemsUrl}
        />,
        node
    );
};


mount();
