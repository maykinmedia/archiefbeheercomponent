import React, {useState, useEffect, useContext} from "react";
import axios from "axios";

import {HiddenInput, TextInput} from "../../forms/inputs";
import {ReviewItemFormset} from "./review-item-formset";
import {ConstantsContext, SuggestionContext} from "./context";
import {SelectInput, SelectWithCustomOption} from "../../forms/select";

const STATUS_TO_BUTTON = {
    "approved": "Accorderen",
    "changes_requested": "Aanpassen",
    "rejected": "Afwijzen",
};


const ReviewForm = ({ itemsUrl, destructionList, reviewComment, reviewChoices }) => {
    const { zaakDetailPermission } = useContext(ConstantsContext);

    // load list items
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [items, setItems] = useState([]);
    const [suggestions, setSuggestions] = useState([]);

    const areThereSuggestions = () => {
      return (suggestions.filter((value) => value).length);
    };

    const [reviewStatus, setReviewStatus] = useState(areThereSuggestions() ? "changes_requested" : "approved");

    useEffect(() => {
        if (areThereSuggestions()) {
            setReviewStatus("changes_requested");
        } else {
            setReviewStatus("approved");
        }
    }, [suggestions]);

    // fetch list items
    useEffect(() => {
        axios.get(itemsUrl)
            .then(
                (result) => {
                    setIsLoaded(true);
                    if (result.data.error) {
                        setError(result.data.error);
                    } else {
                        setItems(result.data.items);
                        setSuggestions(new Array(result.data.items.length).fill(""));
                    }
                },
                (error) => {
                    setIsLoaded(true);
                    setError(error.message);
                }
            );
    }, []);

    const getReviewComment = () => {
        if (reviewComment){
            return (
                <div className="review-create__review-comment">
                    <div className={"header"}>{`${reviewComment.author} heeft een opmerking achtergelaten`}</div>
                    <div className={"text"}>
                        <i className="material-icons">comment &nbsp;</i>
                        {reviewComment.text}
                    </div>
                </div>
            );
        }
    };

    const submitButtons = () => {
        // If the reviewer cannot see zaak details, then
        // they can only accept or reject the list (they can't add suggestions)
        if(zaakDetailPermission === "False") {
            return (
                <div className="review-create__btns">
                    <button
                        type="submit"
                        className="btn"
                        disabled={!isLoaded}
                        onClick={(e) => {
                            setReviewStatus("rejected");
                        }}
                    >{STATUS_TO_BUTTON["rejected"]}</button>
                    <button
                        type="submit"
                        className="btn"
                        disabled={!isLoaded}
                        onClick={(e) => {
                            setReviewStatus("approved");
                        }}
                    >{STATUS_TO_BUTTON["approved"]}</button>
                </div>
            );
        } else {
            return (
                <button
                    type="submit"
                    className="review-create__btn btn"
                    disabled={!isLoaded}
                >{STATUS_TO_BUTTON[reviewStatus]}</button>
            );
        }
    };

    return (
        <SuggestionContext.Provider value={{suggestions, setSuggestions}}>
            {submitButtons()}
            <header className="review-create__header">
                <div>
                    <h1 className="title">{`Lijst "${destructionList.name}"`}</h1>
                    <span className="review-create__list-details">
                        {`${destructionList.created} geleden aangemaakt door ${destructionList.author}`}
                    </span>
                </div>
            </header>

            {getReviewComment()}

            <div className="review-create__comment">
                <SelectWithCustomOption
                    name="text"
                    id="id_text"
                    required={reviewStatus !== "approved"}
                    choices={reviewChoices}
                    label="Opmerkingen"
                    customOtherChoiceLabel={'Anders'}
                />
            </div>

            <HiddenInput
                name="status"
                value={reviewStatus}
            />

            <section className="list-items">
                <h2 className="list-items__header section-title">Zaakdossiers</h2>

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
