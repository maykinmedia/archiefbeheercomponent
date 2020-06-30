import React from "react";

const ConstantsContext = React.createContext({
    prefix: "formset",
    zaakDetailUrl: "",
    zaakDetailPermission: "",
});

const SuggestionContext = React.createContext({
    suggestions: [],
    setSuggestions: undefined,
});

export { ConstantsContext, SuggestionContext };
