// https://github.com/tayiorbeii/egghead.io_idiomatic_redux_course_notes/blob/master/16-Wrapping_dispatch_to_Recognize_Promises.md#adding-promise-support
const addPromiseSupportToDispatch = (store) => {
    const rawDispatch = store.dispatch;
    return (action) => {
        if (typeof action.then === 'function') {
            return action.then(rawDispatch);
        }
        return rawDispatch(action);
    };
};

export default addPromiseSupportToDispatch;
