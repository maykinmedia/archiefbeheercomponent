import React, {useState, useEffect, useContext} from 'react';
import useAsync from 'react-use/esm/useAsync';
import PropTypes from 'prop-types';

import {HiddenInput} from '../../forms/inputs';
import {ReviewItemFormset} from './review-item-formset';
import {ConstantsContext, SuggestionContext} from './context';
import {SelectWithCustomOption} from '../../forms/select';
import {get} from '../../utils/api';

const STATUS_TO_BUTTON = {
    'approved': 'Accorderen',
    'changes_requested': 'Aanpassen',
    'rejected': 'Afwijzen',
};


const ReviewForm = ({ itemsUrl, destructionList, reviewComment, reviewChoices }) => {
    const { zaakDetailPermission } = useContext(ConstantsContext);

    // load list items
    const [error, setError] = useState(null);
    const [items, setItems] = useState([]);
    const [suggestions, setSuggestions] = useState([]);

    const areThereSuggestions = () => {
      return (suggestions.filter((value) => value).length);
    };

    const [reviewStatus, setReviewStatus] = useState(areThereSuggestions() ? 'changes_requested' : 'approved');

    useEffect(() => {
        if (areThereSuggestions()) {
            setReviewStatus('changes_requested');
        } else {
            setReviewStatus('approved');
        }
    }, [suggestions]);

    const {loading} = useAsync( async () => {
        const response = await get(itemsUrl);

        if (!response.ok) {
            setError(response.data);
            return;
        }

        if (response.data.error) {
            setError(response.data.error);
        } else {
            setItems(response.data.items);
            setSuggestions(new Array(result.data.items.length).fill(''));
        }
    }, []);

    return (
        <SuggestionContext.Provider value={{suggestions, setSuggestions}}>
            {
                zaakDetailPermission === 'False'
                ? (
                    <div className="review-create__btns">
                        <button
                            type="submit"
                            className="btn"
                            disabled={loading}
                            onClick={(e) => {
                                setReviewStatus('rejected');
                            }}
                        >{STATUS_TO_BUTTON['rejected']}</button>
                        <button
                            type="submit"
                            className="btn"
                            disabled={loading}
                            onClick={(e) => {
                                setReviewStatus('approved');
                            }}
                        >{STATUS_TO_BUTTON["approved"]}</button>
                    </div>)
                : (
                    <button
                        type="submit"
                        className="review-create__btn btn"
                        disabled={loading}
                    >{STATUS_TO_BUTTON[reviewStatus]}</button>
                )
            }
            <header className="review-create__header">
                <div>
                    <h1 className="title">{`Vernietigingslijst "${destructionList.name}"`}</h1>
                    <span className="review-create__list-details">
                        {`${destructionList.created} geleden aangemaakt door ${destructionList.author}`}
                    </span>
                </div>
            </header>

            {
                reviewComment && (
                    <div className="review-create__review-comment">
                        <div className="header">{`${reviewComment.author} heeft een opmerking achtergelaten`}</div>
                        <div className="text">
                            <i className="material-icons">comment &nbsp;</i>
                            {reviewComment.text}
                        </div>
                    </div>
                )
            }

            <div className="review-create__comment">
                <SelectWithCustomOption
                    name="text"
                    id="id_text"
                    required={reviewStatus !== 'approved'}
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
                    isLoaded={!loading}
                    items={items}
                />
            </section>
        </SuggestionContext.Provider>
    )
};


ReviewForm.propTypes = {
    itemsUrl: PropTypes.string.isRequired,
    destructionList: PropTypes.object.isRequired,
    reviewComment: PropTypes.string,
    reviewChoices: PropTypes.array
};


export { ReviewForm };
