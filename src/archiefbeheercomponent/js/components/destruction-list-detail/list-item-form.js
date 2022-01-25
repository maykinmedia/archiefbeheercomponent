import React, {useContext} from 'react';
import {useImmerReducer} from 'use-immer';
import PropTypes from 'prop-types';

import {HiddenInput} from '../../forms/inputs';
import {FormsetConfigContext, CanUpdateContext} from './context';
import {ListItemModal} from './list-item-modal';
import {ActionIcon} from '../../forms/action-icon';


const INITIAL_STATE = {
    modalIsOpen: false,
    action: '',
    archiefnominatie: '',
    archiefactiedatum: '',
};


const reducer = (draft, action) => {
    switch (action.type) {
        case 'UPDATE_STATE': {
            const updatedDetails = action.payload;

            for (const item in updatedDetails) {
                draft[item] = updatedDetails[item];
            }
            break;
        }
        default: {
          throw new Error(`Unknown action ${action.type}`);
        }
    }
};


const ListItemForm = ({ index, data }) => {
    const { listItem, zaak }  = data;

    const [state, dispatch] = useImmerReducer(reducer, {
        ...INITIAL_STATE,
        archiefnominatie: zaak.archiefnominatie,
        archiefactiedatum: zaak.archiefactiedatum,
    });

    const formsetConfig = useContext(FormsetConfigContext);
    const canUpdate = useContext(CanUpdateContext);

    const prefix = formsetConfig.prefix;
    const id_prefix = (field) => `id_${prefix}-${index}-${field}`;
    const name_prefix = (field) => `${prefix}-${index}-${field}`;

    const getExtraClasses = () => {
        if (!canUpdate) {
            return '';
        }

        let classes = ' list-item--clickable';

        if (state.action) {
            classes += ' list-item--disabled';
        } else if (listItem.review_suggestion) {
            classes += ' list-item--disabled';
        }

        return classes;
    };

    return (
        <>
            <tr
                className={'list-item' + getExtraClasses()}
                onClick={() => {
                    if (canUpdate) {
                        dispatch({type: 'UPDATE_STATE', payload: {modalIsOpen: true}})
                    }
                }}
            >
                <td className="table__hidden">
                    <HiddenInput
                        id={id_prefix('id')}
                        name={name_prefix('id')}
                        value={listItem.id}
                    />
                </td>
                <td>{ zaak.identificatie }</td>
                <td>{`${zaak.zaaktype.omschrijving} (${zaak.zaaktype.versiedatum})`}</td>
                <td>{ zaak.omschrijving }</td>
                <td>{ zaak.looptijd }</td>
                <td>{ zaak.verantwoordelijkeOrganisatie }</td>
                <td>{ zaak.resultaat ? zaak.resultaat.resultaattype.omschrijving : '-' }</td>
                <td>{ zaak.resultaat ? zaak.resultaat.resultaattype.archiefactietermijn : '-'}</td>
                <td>{ zaak.zaaktype.selectielijstProcestype ? zaak.zaaktype.selectielijstProcestype.nummer : '-' }</td>
                <td>{ zaak.relevanteAndereZaken.length > 0 ? 'Ja' : 'Nee' }</td>
                <td>{ listItem.status }</td>
                <td>
                    <ActionIcon action={state.action}/>
                    <HiddenInput
                        id={id_prefix('action')}
                        name={name_prefix('action')}
                        value={state.action}
                    />
                </td>
                <td className="table__hidden">
                    <HiddenInput
                        id={id_prefix('archiefnominatie')}
                        name={name_prefix('archiefnominatie')}
                        value={state.archiefnominatie}
                    />
                    <HiddenInput
                        id={id_prefix('archiefactiedatum')}
                        name={name_prefix('archiefactiedatum')}
                        value={state.archiefactiedatum}
                    />
                    <HiddenInput
                        id={id_prefix('identificatie')}
                        name={name_prefix('identificatie')}
                        value={zaak.identificatie}
                    />
                </td>
            </tr>
            <ListItemModal
                modalIsOpen={state.modalIsOpen}
                listItem={listItem}
                zaak={zaak}
                archiefnominatie={state.archiefnominatie}
                archiefactiedatum={state.archiefactiedatum}
                onChange={(data) => dispatch({type: 'UPDATE_STATE', payload: data})}
            />
        </>
    );
};


ListItemForm.propTypes = {
    index: PropTypes.number,
    data: PropTypes.object,
}


export { ListItemForm };
