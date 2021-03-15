class Hero {
    static setAccess(heroAccess) {
        window.localStorage.setItem("hero-access", heroAccess);
    }

    static hasPrivateAccess() {
        return window.localStorage.getItem("hero-access") === "true";
    }

    static getUrl(id) {
        return this.hasPrivateAccess()
            ? `http://heronet.epa.gov/heronet/index.cfm?action=reference.details&reference_id=${id}`
            : `http://hero.epa.gov/hero/index.cfm?action=reference.details&reference_id=${id}`;
    }
}

export default Hero;
