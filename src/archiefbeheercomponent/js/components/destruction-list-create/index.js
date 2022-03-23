import React from 'react';
import ReactDOM from 'react-dom';
import Modal from 'react-modal';

import { jsonScriptToVar } from '../../utils';
import { DestructionForm } from './destruction-form';
import { ShortReviewZaaktypesContext, ReviewersContext } from './context';
import { UrlsContext } from '../context';
import ErrorBoundary from '../ErrorBoundary';


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
            <ReviewersContext.Provider value={reviewers}>
                <UrlsContext.Provider value={{archiveUpdateUrl: archiveUpdateUrl}}>
                    <ErrorBoundary>
                        <DestructionForm
                            zaaktypen={zaaktypen}
                            zakenUrl={zakenUrl}
                            url={url}
                            currentDate={currentDate}
                            csrftoken={csrftoken}
                        />
                    </ErrorBoundary>
                </UrlsContext.Provider>
            </ReviewersContext.Provider>
        </ShortReviewZaaktypesContext.Provider>,
        node
    );
};


mount();
