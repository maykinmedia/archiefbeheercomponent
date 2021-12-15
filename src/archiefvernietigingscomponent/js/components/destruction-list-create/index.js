import React from 'react';
import ReactDOM from 'react-dom';
import Modal from 'react-modal';

import { jsonScriptToVar } from '../../utils';
import { DestructionForm } from './destruction-form';
import { ShortReviewZaaktypesContext } from './context';
import { ArchiveUpdateUrlContext } from '../context';


const mount = () => {
    const node = document.getElementById('react-destruction-list');
    if (!node) return;

    const zaaktypen = jsonScriptToVar('zaaktype-choices');
    const reviewers = jsonScriptToVar('reviewer-choices');
    const shortReviewZaaktypes = jsonScriptToVar('short-review-zaaktypes');

    const { zakenUrl, archiveUpdateUrl, url, currentDate, csrftoken } = node.dataset;

    Modal.setAppElement('#react-destruction-list');

    ReactDOM.render(
        <ShortReviewZaaktypesContext.Provider value={shortReviewZaaktypes}>
            <ArchiveUpdateUrlContext.Provider value={archiveUpdateUrl}>
                <DestructionForm
                    zaaktypen={zaaktypen}
                    reviewers={reviewers}
                    zakenUrl={zakenUrl}
                    url={url}
                    currentDate={currentDate}
                    csrftoken={csrftoken}
                />
            </ArchiveUpdateUrlContext.Provider>
        </ShortReviewZaaktypesContext.Provider>,
        node
    );
};


mount();
