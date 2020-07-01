import React from "react";

const ConstantsContext = React.createContext({
    formsetConfig: {},
    zaakDetailUrl: "",
    zaakDetailPermission: "",
});

const SuggestionContext = React.createContext({
    suggestions: [],
    setSuggestions: undefined,
});

export { ConstantsContext, SuggestionContext };
