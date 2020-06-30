import React, {useState, useContext, useEffect} from "react";

import {HiddenInput} from "../../forms/inputs";
import {ReviewItemFormset} from "./review-item-formset";
import {SuggestionContext} from "./context";

const STATUS_TO_BUTTON = {
    "approved": "Approve",
    "changes_requested": "Request Changes"
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
        window.fetch(itemsUrl)
            .then(res => res.json())
            .then(
                (result) => {
                    setIsLoaded(true);
                    setItems(result.items);
                    setSuggestions(new Array(result.items.length).fill(""));
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
