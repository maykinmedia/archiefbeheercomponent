import React, {useContext, useEffect, useState} from "react";
import axios from "axios";

import { ListItemForm } from "./list-item-form";
import { ManagementForm } from "../../forms/management-form";
import { FormsetConfigContext } from "./context";


const ListItemFormset = ({itemsUrl}) => {
    const formsetConfig = useContext(FormsetConfigContext);

    // load list items
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [items, setItems] = useState([]);

    //set up forms
    const forms = items.map(
        (data, index) => <ListItemForm
            key={data.listItem.id}
            index={index}
            data={data}
        />
    );

    // fetch list items
    useEffect(() => {
        axios.get(itemsUrl)
            .then(
                (result) => {
                    setIsLoaded(true);
                    setItems(result.data.items);
                },
                (error) => {
                    setIsLoaded(true);
                    setError(error);
                }
            )
    }, []);

    if (error) {
        return <div>Error in fetching zaken: {error.message}</div>;
    }

    if (!isLoaded) {
        return <div>Loading...</div>;
    }

    return (
        <section className="list-items">
            <h2 className="list-items__header section-title">Zaakdossiers</h2>

            <ManagementForm
                prefix={ formsetConfig.prefix }
                initial_forms={ formsetConfig.INITIAL_FORMS }
                total_forms={ items.length }
                min_num_forms={ formsetConfig.MIN_NUM_FORMS }
                max_num_forms={ formsetConfig.MAX_NUM_FORMS }
            />

            <table className="table">
                <thead>
                    <tr>
                        <th className="table__hidden">List item id</th>
                        <th className="table__header">Identificatie</th>
                        <th className="table__header">Zaaktype</th>
                        <th className="table__header">Omschrijving</th>
                        <th className="table__header">Status</th>
                        <th className="table__hidden">Archief</th>
                    </tr>
                </thead>
                <tbody>
                    { forms }
                </tbody>
            </table>
        </section>
    );

};


export { ListItemFormset };
