var Assessment = function(obj, revision_version){
    // implements requirements for js/hawc_utils Version interface
    // unpack JSON object into Assessment
    for (var i in obj) {
        this[i] = obj[i];
    }
    // convert datetime formats
    this.created = new Date(this.created);
    this.changed = new Date(this.changed);
    this.revision_version = revision_version;
    this.banner = this.revision_version + ': ' + String(this.changed) + ' by ' + this.changed_by;
};

Assessment.field_order = ['name', 'cas', 'year', 'revision_version', 'project_manager',
                          'team_members', 'reviewers', 'editable', 'public',
                          'created', 'changed'];
