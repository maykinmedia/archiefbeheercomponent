import React from "react";

const ConstantsContext = React.createContext({
    formsetConfig: {},
    zaakDetailUrl: "",
    zaakDetailPermission: "",
    showOptionalColumns: "",
});

const SuggestionContext = React.createContext({
    suggestions: [],
    setSuggestions: undefined,
});

export { ConstantsContext, SuggestionContext };
