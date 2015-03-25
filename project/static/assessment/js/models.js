var Assessment = function(obj, revision_version){
    // implements requirements for js/hawc_utils Version interface
    // unpack JSON object into Assessment
    for (var i in obj) {
        this[i] = obj[i];
    }
    // convert datetime formats
    this.created = new Date(this.created);
    this.updated = new Date(this.updated);
    this.revision_version = revision_version;
    this.banner = this.revision_version + ': ' + String(this.updated) + ' by ' + this.changed_by;
};
_.extend(Assessment. {
    field_order: [
        'name', 'cas', 'year', 'revision_version', 'project_manager',
        'team_members', 'reviewers', 'editable', 'public',
        'created', 'updated']
});
