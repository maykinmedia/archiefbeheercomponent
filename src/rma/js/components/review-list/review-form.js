import React, {useState, useEffect} from "react";
import axios from "axios";

import {HiddenInput} from "../../forms/inputs";
import {ReviewItemFormset} from "./review-item-formset";
import {SuggestionContext} from "./context";

const STATUS_TO_BUTTON = {
    "approved": "Accorderen",
    "changes_requested": "Aanpassen"
};


const ReviewForm = ({ itemsUrl, destructionList }) => {
    // load list items
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [items, setItems] = useState([]);
    const [suggestions, setSuggestions] = useState([]);

    const reviewStatus = (suggestions.filter((value) => value).length) ? "changes_requested" : "approved";

    // fetch list items
    useEffect(() => {
        axios.get(itemsUrl)
            .then(
                (result) => {
                    setIsLoaded(true);
                    setItems(result.data.items);
                    setSuggestions(new Array(result.data.items.length).fill(""));
                },
                (error) => {
                    setIsLoaded(true);
                    setError(error);
                }
            )
    }, []);

    return (
        <SuggestionContext.Provider value={{suggestions, setSuggestions}}>
            <button type="submit" className="review-create__btn btn" >{STATUS_TO_BUTTON[reviewStatus]}</button>
            <header className="review-create__header">
                <div>
                    <h1 className="title">{`Lijst "${destructionList.name}"`}</h1>
                    <span>{`created ${destructionList.created} ago by ${destructionList.author}`}</span>
                </div>
            </header>

            <HiddenInput
                name="status"
                value={reviewStatus}
            />

            <section className="review-items">
                <h2 className="review-items__header section-title">Zaakdossiers</h2>

                <ReviewItemFormset
                    error={error}
                    isLoaded={isLoaded}
                    items={items}
                />
            </section>
        </SuggestionContext.Provider>
    )
};


export { ReviewForm };