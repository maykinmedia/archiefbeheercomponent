import React, {useEffect, useState} from "react";
import { TextInput } from "../../forms/inputs";



const ReviewItemForm = ({ index, data }) => {
    return (
        <tr>
            <td>{ data.id }</td>
            <td>{ data.zaak} </td>
            <td>
                <TextInput name={"item_reviews-0-text"} id={"id_item_reviews-0-text"}
                />
            </td>
            <td>Suggestion</td>
        </tr>
    );
};


export { ReviewItemForm };
