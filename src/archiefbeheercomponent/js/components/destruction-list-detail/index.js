import React from 'react';
import ReactDOM from 'react-dom';
import Modal from 'react-modal';

import { jsonScriptToVar } from '../../utils';
import { ListItemFormset } from './list-item-formset';
import { FormsetConfigContext, CanUpdateContext } from './context';
import {TextInput} from '../../forms/inputs';


const mount = () => {
    const node = document.getElementById('react-destruction-list-detail');
    if (!node) return;

    const {itemsUrl, canUpdate} = node.dataset;
    const formsetConfig = jsonScriptToVar('formset-config');

    Modal.setAppElement('#react-destruction-list-detail');

    ReactDOM.render(
        <React.Fragment>
            {
                canUpdate === 'True' && (
                    <div className="destruction-list-detail__review-comment">
                        <TextInput
                            name={"text"}
                            required={false}
                            label={"Opmerkingen"}
                            helpText={"Opmerkingen voor de reviewer"}
                            id={"id_text"}
                        />
                    </div>
                )
            }
            <FormsetConfigContext.Provider value={formsetConfig}>
                <CanUpdateContext.Provider value={canUpdate === 'True'}>
                    <ListItemFormset
                        itemsUrl={itemsUrl}
                    />
                </CanUpdateContext.Provider>
            </FormsetConfigContext.Provider>
        </React.Fragment>,
        node
    )
};


mount();
