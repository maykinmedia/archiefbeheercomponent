import React from "react";

import { ReviewItemForm } from "./review-item-form";
import { ManagementForm } from "../../forms/management-form";


const ReviewItemFormset = ({ error, isLoaded, items, suggestions, setSuggestions }) => {
    const prefix = "item_reviews";

    //set up forms
    const forms = items.map(
        (data, index) => <ReviewItemForm
            key={data.list_item_id}
            index={index}
            data={data}
            suggestions={suggestions}
            setSuggestions={setSuggestions}
        />
    );

    if (error) {
        return <div>Error in fetching zaken: {error.message}</div>;
    }

    if (!isLoaded) {
        return <div>Loading...</div>;
    }

    return (
        <>
            <ManagementForm
                prefix={ prefix}
                initial_forms="0"
                total_forms={ items.length }
                min_num_forms="0"
                max_num_forms="1000"
            />

            <table className="table">
                <thead>
                    <tr>
                        <th className="table__hidden">List item id</th>
                        <th className="table__header">Identificatie</th>
                        <th className="table__header">Zaaktype</th>
                        <th className="table__header">Omschrijving</th>
                        <th className="table__header">Actie</th>
                        <th className="table__hidden">Comment</th>
                    </tr>
                </thead>
                <tbody>
                    { forms }
                </tbody>
            </table>
        </>
    );

};


export { ReviewItemFormset };
