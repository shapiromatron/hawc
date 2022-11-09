import $ from "$";

import MetaProtocol from "./MetaProtocol";
import MetaResult from "./MetaResult";

export default {
    MetaProtocol,
    MetaResult,
    startupMetaProtocolPage: (el, config) => MetaProtocol.displayFullPager($(el), config.id),
    startupMetaResultPage: (el, config) => MetaResult.displayFullPager($(el), config.id),
};
