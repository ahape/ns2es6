namespace Brightmetrics.Admin.VoiceAnalytics.ViewModels {

    const showDescriptionLSKey = Brightmetrics.Admin.VoiceAnalytics.Constants.showDescriptionLSKey + ":profiles";

    type TagCategoryChanges = { addTagCategoryId?: string[], removeTagCategoryId?: string[] };

    interface IProps {
        ruleSets: KnockoutObservableArray<Brightmetrics.VoiceAnalytics.Interfaces.IRuleSet>;
        tagCategories: KnockoutObservableArray<Brightmetrics.VoiceAnalytics.Interfaces.ITagCategory>;
        profiles: KnockoutObservableArray<Brightmetrics.VoiceAnalytics.Interfaces.IProfile>;
        possibleDcgs: KnockoutObservableArray<Brightmetrics.VoiceAnalytics.Interfaces.ITargetingSpec>;
        currentView: KnockoutObservable<Enums.View>;
        onAdd: (profile: Brightmetrics.VoiceAnalytics.Interfaces.IProfile) => Promise<Brightmetrics.VoiceAnalytics.Interfaces.IProfile>;
        onUpdate: (profile: Brightmetrics.VoiceAnalytics.Interfaces.IProfile, tagCategoryChanges: Record<string, any>) => Promise<Brightmetrics.VoiceAnalytics.Interfaces.IProfile>;
        onDelete: (id: string) => Promise<void>;
    }

    function getTargetingRuleFilterValues(targetingRuleFilterId: string, targetDcgId: number)
        : () => Promise<Array<IKoOption<string>>> {
        return () => Utils.ajaxRequest(`/VoiceAnalytics/${defCompanyId}/Profiles` +
              `?getPossibleValues=${targetingRuleFilterId}&targetDcg=${targetDcgId}`)
            .then((response: { data?: string[], commandId?: string; success: boolean }) => {
                if (response.data) {
                    return $.Deferred().resolve({ data: response.data });
                }

                // In the case of querying agent names, queues, etc., a detail
                // query may be issued.
                if (response.commandId) {
                    const defd = $.Deferred<{ data: string[] }>();
                    Utils.waitForCommandData(response.commandId).subscribe((status) => {
                        if (status.data) {
                            defd.resolve({ data: (status.data as string[][]).map((x) => x[0]), });
                        }
                    });
                    return defd.promise();
                }

                throw new Error("Failed to load targeting rule filter");
            })
            .then((response: { data: string[] }) => {
                return response.data
                    .map((value) => ({
                        label: value,
                        value,
                    }))
                    .sort((a, b) => Utils.stringComparer(a.label, b.label));
            });
    }

    export class ManageProfiles extends Brightmetrics.ViewModel {
        public templateId = "manage-profiles-view-template";
        public selectedProfileId: KnockoutObservable<string>;
        /* Used for populating initial value when rendering profile <select> */
        public selectedProfileIdInitialValue : string;
        public profileOptions: KnockoutComputed<Array<IKoOption<string>>>;
        public currentView: KnockoutObservable<Enums.View>;
        public profiles: KnockoutObservableArray<Brightmetrics.VoiceAnalytics.Interfaces.IProfile>;
        public isSaving: KnockoutObservable<boolean>;
        public isDescriptionShowing: KnockoutObservable<boolean>;
        public editor: KnockoutComputed<ProfileEditor>;
        public canSave: KnockoutComputed<boolean>;
        public canDelete: KnockoutComputed<boolean>;

        constructor(props: IProps) {
            super(props);
        }

        private showUnsavedChangesDialog(): Promise<string> {
            return Utils.basicConfirm2({
                content: "Are you sure you want to navigate away from the profile you're editing?" +
                    " All of your changes will be lost.",
                title: "Unsaved Changes",
                buttonLabels: ["DISCARD"],
            });
        }

        initialize(props: IProps) {
            this.isSaving = ko.observable(false);
            this.currentView = props.currentView;
            this.selectedProfileId = ko.observable();
            this.profiles = props.profiles;
            this.isDescriptionShowing = ko.observable(localStorage.getItem(showDescriptionLSKey) !== "false");

            const defaultProfile = _.first(props.profiles.peek());
            if (defaultProfile) {
                this.selectedProfileId(defaultProfile.id);
            }

            this.selectedProfileIdInitialValue = this.selectedProfileId.peek();
        }

        initSubscriptions(props: IProps) {
            this.profileOptions = ko.pureComputed(() => this.profiles().map((p) =>
                ({ label: p.name, value: p.id })));

            this.editor = ko.pureComputed(() => {
                const selectedProfileId = this.selectedProfileId();
                const profile = _.find(this.profiles(), (p) => p.id === selectedProfileId);
                return new ProfileEditor({ ...props, profile, });
            });

            this.canSave = ko.pureComputed(() =>
                !this.isSaving() &&
                this.editor().isValid() &&
                this.editor().hasChanged());

            this.canDelete = ko.pureComputed(() => !this.editor().isNew);
        }

        createEventHandlers(props: IProps) {
            // Helpers for preventing unwanted recursive loops.
            const loopGuards = {
                isDiscarding: false,
                hasPreventedDefault: false,
            };

            this.events.onDescriptionVisibilityToggle = () => {
                const next = !this.isDescriptionShowing();

                this.isDescriptionShowing(next);

                localStorage.setItem(showDescriptionLSKey, String(next));
            };

            this.events.onProfileChange = (data: unknown, event: JQueryInputEventObject) => {
                const element = event.target as HTMLInputElement;
                const nextProfileId = element.value;

                if (loopGuards.hasPreventedDefault) {
                    loopGuards.hasPreventedDefault = false;
                }

                if (!loopGuards.isDiscarding && this.editor().hasChanged()) {
                    this.showUnsavedChangesDialog().then((choice) => {
                        if (choice === "DISCARD") {
                            this.selectedProfileId(nextProfileId);

                            loopGuards.isDiscarding = true;

                            // The optionsCaption value is `undefined`,
                            // but `selectElement.value = undefined` won't change the
                            // option to "SELECT A PROFILE". Instead, it needs to be
                            // an empty string that triggers the change. This is why
                            // the `|| ""`
                            element.value = nextProfileId || "";
                        }
                    });

                    loopGuards.hasPreventedDefault = true;

                    element.value = this.selectedProfileId() || "";
                } else {
                    loopGuards.isDiscarding = false;

                    this.selectedProfileId(nextProfileId);
                }
            };

            this.events.onViewChangeClick = (data: unknown, event: JQueryInputEventObject) => {
                const view = (event.target as HTMLElement)
                    .innerText
                    .replace(/\s+/g, "") as Enums.View;

                // If the user tries to navigate away from this view while changes
                // have been made, then they should be prompted if they would like to
                // discard those changes or stay in this view.
                if (this.editor().hasChanged()) {
                    this.showUnsavedChangesDialog().then((choice) => {
                        if (choice === "DISCARD") {
                            this.currentView(view);
                        }
                    });
                } else {
                    this.currentView(view);
                }
            };

            this.events.onSaveClick = () => {
                if (this.canSave()) {
                    let request: Promise<void>;
                    const editor = this.editor();
                    const json = editor.toJSON();

                    this.isSaving(true);
                    const after = () => this.isSaving(false);

                    if (editor.isNew) {
                        request = props.onAdd(json).then(
                            () => Utils.notifyUser("Successfully added profile " + json.name, ["success"]),
                            () => Utils.notifyUser("Failed to add profile " + json.name, ["error"]));
                    } else {
                        request = props.onUpdate(json, editor.tagCategoryChanges()).then(
                            () => Utils.notifyUser("Successfully updated profile " + json.name, ["success"]),
                            () => Utils.notifyUser("Failed to update profile " + json.name, ["error"]));
                    }

                    request.then(after, after);
                }
            };

            this.events.onDeleteClick = () => {
                if (this.canDelete()) {
                    const json = this.editor().toJSON();

                    Utils.basicConfirm2({
                        content: "Are you sure you want to delete the profile " + json.name,
                        title: "Delete Profile " + json.name,
                    }).then((choice) => {
                        if (choice === "OKAY") {
                            props.onDelete(json.id).then(
                                () => Utils.notifyUser("Successfully deleted profile " + json.name, ["success"]),
                                () => Utils.notifyUser("Failed to delete profile " + json.name, ["error"]));
                        }
                    });

                }
            };
        }
    }

    interface IProfileEditorProps {
        profile?: Brightmetrics.VoiceAnalytics.Interfaces.IProfile;
        possibleDcgs: KnockoutObservableArray<Brightmetrics.VoiceAnalytics.Interfaces.ITargetingSpec>;
        tagCategories: KnockoutObservableArray<Brightmetrics.VoiceAnalytics.Interfaces.ITagCategory>;
    }

    // tslint:disable:max-classes-per-file
    class ProfileEditor extends Brightmetrics.ViewModel {
        private _id: string;
        private _dataSourceInstanceId: number;
        private _nameHasBlurred: KnockoutObservable<boolean>;
        /** Used for comparison when determining if the user has pending changes */
        private _initialState: Brightmetrics.VoiceAnalytics.Interfaces.IProfile;
        private _dcgTypesThatCanDoNative: KnockoutObservableArray<number>;
        public isNew: boolean;
        public name: KnockoutObservable<string>;
        public nameHasFocus: KnockoutObservable<boolean>;
        public nameHasError: KnockoutComputed<boolean>;
        // TODO: Get tooltip for targeting rules.
        public targetingRulesTooltip: string = "This is the targeting rules tooltip";
        // TODO: Get tooltip for tag categories.
        public tagCategoriesTooltip: string = "This is the tag categories tooltip";
        public dataSourceOptions: KnockoutComputed<Array<IKoOption<number>>>;
        public selectedDataSourceGroupId: KnockoutObservable<number>;
        public disableDataSourceSelection: boolean;
        public targetingRules: KnockoutObservableArray<TargetingRule>;
        public tagCategories: KnockoutObservableArray<TagCategory>;
        public useNativeTranscription: KnockoutObservable<boolean>;
        public canDoNativeTranscription: KnockoutComputed<boolean>;
        public isValid: KnockoutComputed<boolean>;
        public hasChanged: KnockoutComputed<boolean>;
        public tagCategoryChanges: KnockoutComputed<TagCategoryChanges>;

        constructor(props: IProfileEditorProps) {
            super(props);
        }

        private _createKoPossibleTargetingRuleFilters(props: IProfileEditorProps)
            : KnockoutComputed<Brightmetrics.VoiceAnalytics.Interfaces.ITargetingRuleSpec[]> {
            // Computed because things may not have loaded yet (?).
            return ko.pureComputed(() => {
                const targetSpec = _.find(props.possibleDcgs(), (d) => d.id === this.selectedDataSourceGroupId());

                if (targetSpec) {
                    return targetSpec.targetingRuleSpecs;
                }

                return [];
            });
        }

        private _updateTagCategories(allTagCategories: Brightmetrics.VoiceAnalytics.Interfaces.ITagCategory[]): Promise<Brightmetrics.VoiceAnalytics.Interfaces.ITagCategory[]> {
            const defd = $.Deferred<Brightmetrics.VoiceAnalytics.Interfaces.ITagCategory[]>();
            const dialog: Brightmetrics.MultipleSelect.ViewModels.MultipleSelectDialog<string> = new Brightmetrics.MultipleSelect.ViewModels.MultipleSelectDialog<string>({
                listFetcher: () => $.Deferred().resolve({ data: allTagCategories })
                    .then((response: { data: Brightmetrics.VoiceAnalytics.Interfaces.ITagCategory[]; }) => {
                        return response.data
                            .map((tc, i) => ({ label: tc.name, value: tc.id }))
                            .sort((a, b) => Utils.stringComparer(a.label, b.label));
                    }),
                listLabels: ["Tag Category"],
                nameForItem: "Tag Category",
                onUpdate: (data) => {
                    defd.resolve(data.values.map((o) => {
                        return _.find(allTagCategories, (tc) => tc.id === o.value)!;
                    }));
                },
                presetValues: this.tagCategories.peek().map((tcvm) => tcvm.id),
            });

            /*
            dialog.onClose = () => {
                if (defd.state() !== "resolved") {
                    defd.reject();
                }
            };
            */

            dialog.open();

            return defd.promise();
        }

        initialize(props: IProfileEditorProps) {
            this._dataSourceInstanceId = 0;

            const possibleDcgs = props.possibleDcgs.peek();

            this._dcgTypesThatCanDoNative = ko.observableArray(possibleDcgs
                .filter((d) => d.canUseNativeTranscription)
                .map((d) => d.id));

            // Need to presupply this component with the target dcgs
            //
            // This will also function as supplying possible targeting rule filters
            // along with their values
            this.selectedDataSourceGroupId = ko.observable(
                possibleDcgs.length > 0 ?  possibleDcgs[0].id : 0);
            this.name = ko.observable("");
            this.nameHasFocus = ko.observable(false);
            this._nameHasBlurred = ko.observable(false);
            this.disableDataSourceSelection = false;
            this.targetingRules = ko.observableArray();
            this.tagCategories = ko.observableArray();
            this.useNativeTranscription = ko.observable(false);
            this.isNew = true;

            if (props.profile) {
                this._id = props.profile.id;
                this._dataSourceInstanceId = props.profile.dataSourceInstanceId;
                this.isNew = false;

                this.name(props.profile.name);
                this.disableDataSourceSelection = true;
                this.selectedDataSourceGroupId(props.profile.targetDataConnectionGroupId);
                this.useNativeTranscription(props.profile.useNativeTranscription);
                this.targetingRules(props.profile.targetingRules.map((targetingRule) =>
                    new TargetingRule({
                        ...props,
                        targetDcg: props.profile!.targetDataConnectionGroupId,
                        possibleTargetingRuleFilters: this._createKoPossibleTargetingRuleFilters(props),
                        targetingRule,
                    })));

                this.tagCategories(props.profile.tagCategories.map((id) => {
                    const tagCategory =  _.find(props.tagCategories.peek(), (tc) => tc.id === id);

                    if (!tagCategory) {
                        return null;
                    }

                    return new TagCategory({
                        tagCategory,
                        onDelete: (t) => this.tagCategories.remove(t),
                    });
                }).filter((tcvm) => tcvm != null) as TagCategory[]);
            }
        }

        initSubscriptions(props: IProfileEditorProps) {
            // In case our options list updates and subsequently auto-updates the selected DCG
            // causing there to be a "new pending state". This circumvents that.
            props.possibleDcgs.subscribe((dcgs) => {
                if (this.isNew && dcgs.length > 0) {
                    this._initialState.targetDataConnectionGroupId = dcgs[0].id;
                }

                this._dcgTypesThatCanDoNative(dcgs
                    .filter((d) => d.canUseNativeTranscription)
                    .map((d) => d.id));
            });

            this.selectedDataSourceGroupId.subscribe((newId) => {
                // If composing a new Profile, and the user changes the
                // underlying target platform, then wipe all their stuff.
                if (this.isNew) {
                    this.targetingRules.removeAll();
                    this.tagCategories.removeAll();
                }
            });

            this.canDoNativeTranscription = ko.pureComputed(() =>
                _.contains(this._dcgTypesThatCanDoNative(), this.selectedDataSourceGroupId()));

            this.dataSourceOptions = ko.pureComputed(() => props.possibleDcgs().map((d) => {
                const gtype = d.id;
                return {
                    label: _.find(dataConnectionGroups, (dcg) => dcg.Id === gtype)!.Name,
                    value: gtype,
                };
            }));

            // If the name input is focused into and then blurred, then we
            // want to show any error styling. This logic assists with that.
            this.nameHasFocus.subscribe((has) => {
                if (!has && !this._nameHasBlurred()) {
                    this._nameHasBlurred(true);
                }
            });

            this.nameHasError = ko.pureComputed(() => {
                return this._nameHasBlurred() && this.name().trim() === "";
            });

            this.isValid = ko.pureComputed(() => {
                const targetingRules = this.targetingRules();

                return this.name().trim() !== "" &&
                    this.selectedDataSourceGroupId() != null &&
                    targetingRules.length > 0 &&
                    targetingRules.every((trvm) => trvm.isValid());
            });

            props.tagCategories.subscribe((updatedList) => {
                this.tagCategories((props.profile ? props.profile.tagCategories : []).map((id) => {
                    const tagCategory =  _.find(updatedList, (tc) => tc.id === id)!;

                    return new TagCategory({
                        tagCategory,
                        onDelete: (t) => this.tagCategories.remove(t),
                    });
                }));
            });

            this.tagCategoryChanges = ko.pureComputed(() => {
                const previous = this._initialState.tagCategories;
                const current = this.toJSON().tagCategories;
                const comparison = ko.utils.compareArrays(previous, current);
                const obj = {} as TagCategoryChanges;
                const added = comparison.filter((c) => c.status === "added").map((c) => c.value);
                const deleted =  comparison.filter((c) => c.status === "deleted").map((c) => c.value);
                if (added.length > 0) {
                    obj.addTagCategoryId = added;
                }
                if (deleted.length > 0) {
                    obj.removeTagCategoryId = deleted;
                }
                return obj;
            });

            ko.ignoreDependencies(() => { this._initialState = this.toJSON(); });

            this.hasChanged = ko.pureComputed(() => !_.isEqual(this.toJSON(), this._initialState));
        }

        createEventHandlers(props: IProfileEditorProps) {
            this.events.onAddTargetingRuleClick = () => {
                this.targetingRules.push(new TargetingRule({
                    ...props,
                    possibleTargetingRuleFilters: this._createKoPossibleTargetingRuleFilters(props),
                    targetDcg: this.selectedDataSourceGroupId(),
                    targetingRule: {
                        targetingRuleFilters: [],
                        transcriptionPercent: 100,
                    },
                }));
            };

            this.events.onDeleteTargetingRuleClick = (targetingRule: TargetingRule) => {
                this.targetingRules.remove(targetingRule);
            };

            this.events.onAddTagCategoryClick = () => {
                this._updateTagCategories(props.tagCategories()).then((updatedList) => {
                    this.tagCategories(updatedList.map((tagCategory) => {
                        return new TagCategory({
                            tagCategory,
                            onDelete: (t) => this.tagCategories.remove(t),
                        });
                    }));
                });
            };
        }

        toJSON(): Brightmetrics.VoiceAnalytics.Interfaces.IProfile {
            return {
                id: this._id,
                name: this.name(),
                targetingRules: this.targetingRules().map((tr) => tr.toJSON()),
                dataSourceInstanceId: this._dataSourceInstanceId,
                targetDataConnectionGroupId: this.selectedDataSourceGroupId(),
                tagCategories: this.tagCategories().map((tc) => tc.id),
                useNativeTranscription: this.useNativeTranscription(),
            };
        }
    }

    interface ITargetingRuleProps {
        targetDcg: number;
        targetingRule: Brightmetrics.VoiceAnalytics.Interfaces.ITargetingRule;
        possibleTargetingRuleFilters: KnockoutComputed<Brightmetrics.VoiceAnalytics.Interfaces.ITargetingRuleSpec[]>;
    }

    // tslint:disable:max-classes-per-file
    class TargetingRule extends Brightmetrics.ViewModel {
        public filters: KnockoutObservableArray<TargetingRuleFilter>;
        public transcriptionPercent: KnockoutObservable<number>;
        public isTranscriptionPercentValid: KnockoutComputed<boolean>;
        public isValid: KnockoutComputed<boolean>;

        constructor(props: ITargetingRuleProps) {
            super(props);
        }

        private _addFilterDialog(props: ITargetingRuleProps): Brightmetrics.ViewModels.DialogViewModel {
            const filterValuesById: { [id: string]: KnockoutObservableArray<string> } = {};

            props.possibleTargetingRuleFilters.peek().forEach((trf) => {
                filterValuesById[trf.id] = ko.observableArray();
            });

            const presetValues: string[] = [];

            // Populate the dictionary.
            this.filters.peek().map((trf) => {
                const id = trf.id;
                const values = trf.values.peek().slice();

                presetValues.push(id);

                filterValuesById[id](values);
            });

            const dialog: Brightmetrics.MultipleSelect.ViewModels.MultipleSelectDialog<string> = new Brightmetrics.MultipleSelect.ViewModels.MultipleSelectDialog<string>({
                listFetcher: () => $.Deferred().resolve({ data: props.possibleTargetingRuleFilters.peek() })
                    .then((response: { data: Brightmetrics.VoiceAnalytics.Interfaces.ITargetingRuleSpec[]; }) => {
                        return response.data
                            .map((trfs, i) => ({
                                label: trfs.name,
                                value: trfs.id,
                            }))
                            .sort((a, b) => Utils.stringComparer(a.label, b.label));
                    }),
                listLabels: ["Targeting Rule Filter"],
                nameForItem: "Targeting Rule Filter",
                // data: { values: string[] }
                onUpdate: (data) => {
                    this.filters(data.values.map((o) => {
                        return new TargetingRuleFilter({
                            ...props,
                            filter: {
                                targetingRuleFilterId: o.value,
                                filterValues: filterValuesById[o.value].slice(0),
                            },
                            onDelete: (f) => this.filters.remove(f),
                        });
                    }));
                },
                presetValues,
                // opts: { label: string; value: number }
                pillFactory: (opts) => {
                    const list = filterValuesById[opts.value];

                    return new SubPill<string>({
                        label: opts.label as string,
                        value: opts.value as any,
                        parentDialog: dialog,
                        onUpdate: (updated) => { list(updated); },
                        innerListFetcher: getTargetingRuleFilterValues(opts.value, props.targetDcg),
                        innerListLabel: "Targeting Rule Filter Values",
                        presetValues: () => list.peek(),
                        pillLabel: ko.pureComputed(() => opts.label + ": " + list().join(", ")),
                    }) as any; // FIXME: Sucks to resort to `any`, but it's a limitation of the base class.
                }
            });

            dialog.open();

            return dialog;
        }

        initialize(props: ITargetingRuleProps) {
            this.transcriptionPercent = ko.observable(props.targetingRule.transcriptionPercent);
            this.filters = ko.observableArray(props.targetingRule.targetingRuleFilters.map((filter) =>
                new TargetingRuleFilter({
                    ...props,
                    filter,
                    onDelete: (f) => this.filters.remove(f),
                })));
        }

        initSubscriptions(props: ITargetingRuleProps) {
            this.isTranscriptionPercentValid = ko.pureComputed(() => {
                const transcriptionPercent = parseFloat(this.transcriptionPercent() as any);

                return !isNaN(transcriptionPercent) && transcriptionPercent > 0 && transcriptionPercent <= 100;
            });

            this.isValid = ko.pureComputed(() => {
                return this.isTranscriptionPercentValid() &&
                    this.filters().every((fvm) => fvm.isValid());
            });
        }

        createEventHandlers(props: ITargetingRuleProps) {
            this.events.onAddFilterClick = () => {
                this._addFilterDialog(props);
            };
        }

        toJSON(): Brightmetrics.VoiceAnalytics.Interfaces.ITargetingRule {
            return {
                // Parsing as float because KO textinput often stringifies value.
                transcriptionPercent: parseFloat(this.transcriptionPercent() as any),
                targetingRuleFilters: this.filters().map((fvm) => fvm.toJSON()),
            };
        }
    }

    interface ITargetingRuleFilterProps {
        targetDcg: number;
        filter: Brightmetrics.VoiceAnalytics.Interfaces.ITargetingRuleFilter;
        possibleTargetingRuleFilters: KnockoutComputed<Brightmetrics.VoiceAnalytics.Interfaces.ITargetingRuleSpec[]>;
        onDelete: (filter: TargetingRuleFilter) => void;
    }

    // tslint:disable:max-classes-per-file
    class TargetingRuleFilter extends Brightmetrics.ViewModel {
        public id: string;
        public label: string;
        public values: KnockoutObservableArray<string>;
        public isValid: KnockoutComputed<boolean>;

        constructor(props: ITargetingRuleFilterProps) {
            super(props);
        }

        initialize(props: ITargetingRuleFilterProps) {
            const targetingRuleFilter = _.find(props.possibleTargetingRuleFilters.peek(), (f) =>
                f.id === props.filter.targetingRuleFilterId)!;

            this.id = targetingRuleFilter.id;
            this.label = targetingRuleFilter.name;
            this.values = ko.observableArray(props.filter.filterValues);
        }

        initSubscriptions(props: ITargetingRuleFilterProps) {
            this.isValid = ko.pureComputed(() => {
                return this.values().length > 0;
            });
        }

        createEventHandlers(props: ITargetingRuleFilterProps) {
            this.events.onDeleteClick = () => props.onDelete(this);

            this.events.onClick = () => {
                const dialog: Brightmetrics.MultipleSelect.ViewModels.MultipleSelectDialog<string> = new Brightmetrics.MultipleSelect.ViewModels.MultipleSelectDialog<string>({
                    listFetcher: getTargetingRuleFilterValues(this.id, props.targetDcg),
                    listLabels: ["Targeting Rule Filter Values"],
                    nameForItem: "Targeting Rule Filter Values",
                    onUpdate: (data) => {
                        this.values(data.values.map((o) => o.value));
                    },
                    presetValues: this.values.slice(0),
                });

                dialog.open();

                return dialog;
            };
        }

        toJSON(): Brightmetrics.VoiceAnalytics.Interfaces.ITargetingRuleFilter {
            return {
                targetingRuleFilterId: this.id,
                filterValues: this.values(),
            };
        }
    }

    interface ITagCategoryProps {
        tagCategory: Brightmetrics.VoiceAnalytics.Interfaces.ITagCategory;
        onDelete: (tagCategory: TagCategory) => void;
    }

    // tslint:disable:max-classes-per-file
    class TagCategory extends Brightmetrics.ViewModel {
        public id: string;
        public label: string;
        public tags: KnockoutObservableArray<Brightmetrics.VoiceAnalytics.Interfaces.IRuleSetTag>;

        constructor(props: ITagCategoryProps) {
            super(props);
        }

        private _loadRuleSetTags() {
            return Utils.ajaxRequest(`/VoiceAnalytics/${defCompanyId}/TagCategories/${this.id}/RuleSetTags`)
                .then((response: { success: boolean; ruleSetTags: Brightmetrics.VoiceAnalytics.Interfaces.IRuleSetTag[] }) => {
                    if (response.success) {
                        this.tags(response.ruleSetTags);
                    }
                });
        }

        initialize(props: ITagCategoryProps) {
            this.id = props.tagCategory.id;
            this.label = props.tagCategory.name;
            this.tags = ko.observableArray();

            this._loadRuleSetTags();
        }

        createEventHandlers(props: ITagCategoryProps) {
            this.events.onDeleteClick = () => props.onDelete(this);
        }
    }
}
