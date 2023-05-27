namespace Brightmetrics.Admin.ViewModels {
    import BEs = Brightmetrics.Enums;
    import BIs = Brightmetrics.Interfaces;
    import BVs = Brightmetrics.ViewModels;
    import BISIs = Brightmetrics.Insights.Scorecards.Interfaces;
    import BDIs = Brightmetrics.Dashboard.Interfaces;
    import BRIDs = Brightmetrics.Reports.Interfaces.DTOs;

    const tabPermissionLevels = [
        "None",
        "View",
        "Modify",
        "Admin"
    ];

    enum EScheduleTypes {
        Dashboard = "Dashboard",
        Report = "Report",
        Forecast = "Staff Forecasting",
        Scorecard = "Scorecard"
    }

    type Schedules =
        BIs.IReportSchedule |
        BIs.IDashboardSchedule |
        BIs.IForecastSchedule | BISIs.IScorecardSchedule;

     interface ISchedule {
         accessLevel: number;
         accessLevelName: string;
         destinations: string | string[];
         dsiId: number | null;
         id: string;
         name: string;
         schedule: Schedules;
         scheduleId: number | string;
         summary: string;
         type: EScheduleTypes;
         userId: number;
     }

     interface IScheduleBR {
        dsiId: number | null;
        emailAddress: string;
        schedule: ISchedule;
        user: Interfaces.IOldUserPermission;
     }

     interface ISchedulesByRecipient {
        emailAddress: string;
        schedules: Array<{
            dsiId: number | null;
            emailAddress: string;
            schedule: ISchedule;
            user: any;
        }>;
     }

    interface ISchedulesByUser {
        emailAddress: string;
        schedules: ISchedule[];
        userId: number;
        userName: string;
    }

    interface ISchedulesManagementProps {
        dashboards: KnockoutObservableArray<any>;
        forecasts: KnockoutObservableArray<any>;
        reports: KnockoutObservableArray<Interfaces.IReport>;
        users: KnockoutObservableArray<Interfaces.IOldUserPermission>;
        scorecards: KnockoutObservableArray<BISIs.IScorecardSaved>;
        filter: KnockoutObservable<string>;
        filterHasValue: KnockoutComputed<boolean>;
        loadingReports: KnockoutComputed<boolean>;
        loadingScorecards: KnockoutComputed<boolean>;
        loadingUsers: KnockoutComputed<boolean>;
        loadingDashboards: KnockoutComputed<boolean>;
        loadingForecasts: KnockoutComputed<boolean>;
        loadingSchedules: KnockoutComputed<boolean>;
        onFilterClearClick: () => void;
    }

    const missingUser = {
        emailAddress: "n/a",
        name: "(missing)",
        userId: 0
    };

    export class SchedulesManagement extends ViewModel {
        public view: KnockoutObservable<string>;
        public availableDataSourceGroups: BIs.IDataSourceGroup[];
        public availableGroupsByDSGID: any;

        public dashboards: KnockoutObservableArray<any>;
        public forecasts: KnockoutObservableArray<any>;
        public reports: KnockoutObservableArray<Interfaces.IReport>;
        public scorecards: KnockoutObservableArray<BISIs.IScorecardSaved>;
        public filter: KnockoutObservable<string>;
        public filterHasValue: KnockoutComputed<boolean>;
        public loadingData: KnockoutComputed<boolean>;
        public schedulesByRecipient: KnockoutComputed<ISchedulesByRecipient[]>;
        public schedulesByUser: KnockoutComputed<ISchedulesByUser[]>;

        constructor(props: ISchedulesManagementProps) {
            super(props);
        }

        private getFilterFromURL(): string {
            const parameters = Utils.getQueryParameters();

            return parameters.filter || "";
        }

        public initialize(props: ISchedulesManagementProps) {
            this.view = ko.observable("schedulesbyrecipient");
            this.availableDataSourceGroups = Utils.getAvailableDataSourceGroups();
            this.availableGroupsByDSGID = {};

            this.dashboards = props.dashboards;
            this.forecasts = props.forecasts;
            this.reports = props.reports;
            this.scorecards = props.scorecards;
            this.filter = props.filter;
            this.filterHasValue = props.filterHasValue;

            this.filter(this.getFilterFromURL());
        }

        public initSubscriptions(props: ISchedulesManagementProps) {
            this.loadingData = ko.computed(() =>
                props.loadingDashboards() ||
                props.loadingForecasts() ||
                props.loadingSchedules() ||
                props.loadingUsers() ||
                props.loadingReports() ||
                props.loadingScorecards());

            this.schedulesByRecipient = ko.computed(() => {
                if (this.loadingData()) {
                    return [];
                }

                const users = props.users();
                const scheduleObj: ISchedule[] = [];

                _.forEach(props.dashboards(), (item) => {
                    _.forEach(item.schedules, (s: any) => {
                        scheduleObj.push({
                            accessLevel: item.permissionLevel,
                            accessLevelName: tabPermissionLevels[s.accessLevel],
                            destinations: s.Destinations,
                            dsiId: null,
                            id: item.tabId,
                            name: s.DefaultSubject,
                            scheduleId: s.Id,
                            schedule: s,
                            summary: s.ScheduleSummary,
                            type: EScheduleTypes.Dashboard,
                            userId: item.userId,
                        });
                    });
                });

                _.forEach(props.reports(), (item) => {
                    _.forEach(item.schedules, (s) => {
                        scheduleObj.push({
                            accessLevel: item.accessLevel,
                            accessLevelName: tabPermissionLevels[item.accessLevel],
                            destinations: s.destinations,
                            dsiId: item.templateContent.dataSourceInstance!,
                            id: item.templateId,
                            name: item.templateContent.name,
                            schedule: s,
                            scheduleId: s.id,
                            summary: (s as any).summary,
                            type: EScheduleTypes.Report,
                            userId: item.userId,
                        });
                    });
                });

                _.forEach(props.forecasts(), (item: any) => {
                    scheduleObj.push({
                        accessLevel: 3,
                        accessLevelName: tabPermissionLevels[3],
                        destinations: item.schedule.destinations,
                        dsiId: null,
                        id: item.schedule.id,
                        name: item.schedule.options.groups[0],
                        schedule: item.schedule,
                        scheduleId: item.schedule.id,
                        summary: item.schedule.summary,
                        type: EScheduleTypes.Forecast,
                        userId: item.schedule.userId,
                    });
                });

                _.forEach(props.scorecards(), (item) => {
                    _.forEach(item.schedules, (s) => {
                        if (_.isEmpty(s.destinations) && !_.isEmpty(s.individualScorecardEmail)) {
                            const agents = JSON.parse(s.individualScorecardEmail);

                            _.forEach(agents, (email: string, name: string) => {
                                scheduleObj.push({
                                    accessLevel: item.accessLevel,
                                    accessLevelName: tabPermissionLevels[item.accessLevel],
                                    destinations: email,
                                    dsiId: null,
                                    id: item.id,
                                    name: item.scorecardContent.name,
                                    summary: s.scheduleSummary,
                                    schedule: s,
                                    scheduleId: s.id,
                                    type: EScheduleTypes.Scorecard,
                                    userId: item.userId,
                                });
                            });
                        } else {
                            scheduleObj.push({
                                accessLevel: item.accessLevel,
                                accessLevelName: tabPermissionLevels[item.accessLevel],
                                destinations: s.destinations,
                                dsiId: null,
                                id: item.id,
                                name: item.scorecardContent.name,
                                schedule: s,
                                scheduleId: s.id,
                                summary: s.scheduleSummary,
                                type: EScheduleTypes.Scorecard,
                                userId: item.userId,
                            });
                        }
                    });
                });

                return _.chain(scheduleObj)
                    .map((r) => {
                        const user = _.find(users, (u) => u.userId === r.userId) || missingUser;
                        return {
                            schedule: r,
                            user
                        };
                    })
                    .flatten()
                    .map((s) => _.map(((s.schedule as ISchedule).destinations as string).split(/,\s+/), (d) =>
                            ({
                                dsiId: (s.schedule as ISchedule).dsiId || null,
                                emailAddress: d,
                                schedule: (s.schedule as ISchedule),
                                user: s.user,
                            })))
                    .flatten()
                    .groupBy("emailAddress")
                    .map((schedules, emailAddress: string) => (
                        {
                            emailAddress,
                            schedules: _.sortBy(schedules, (s) => s.emailAddress)
                        }))
                    .filter((obj) => {
                        const email = ko.unwrap(obj.emailAddress);

                        if (!this.filter()) {
                            return true;
                        }

                        return email
                            .toLowerCase()
                            .indexOf(this.filter().toLowerCase()) !== -1;
                    })
                    .sortBy("emailAddress")
                    .value();
            });

            this.schedulesByUser = ko.computed(() => {
                if (this.loadingData()) {
                    return [];
                }

                const users = props.users();
                const scheduleObj: ISchedule[] = [];

                _.forEach(props.dashboards(), (item) => {
                    _.forEach(item.schedules, (s: any) => {
                        scheduleObj.push({
                            accessLevel: item.permissionLevel,
                            accessLevelName: tabPermissionLevels[item.accessLevel],
                            destinations: s.Destinations,
                            dsiId: null,
                            id: item.tabId,
                            name: s.DefaultSubject,
                            schedule: s,
                            scheduleId: s.Id,
                            summary: s.ScheduleSummary,
                            type: EScheduleTypes.Dashboard,
                            userId: item.userId,
                        });
                    });
                });

                _.forEach(props.reports(), (item) => {
                    _.forEach(item.schedules, (s) => {
                        scheduleObj.push({
                            accessLevel: item.accessLevel,
                            accessLevelName: tabPermissionLevels[item.accessLevel],
                            destinations: s.destinations,
                            dsiId: item.templateContent.dataSourceInstance || null,
                            id: item.templateId,
                            name: item.templateContent.name,
                            schedule: s,
                            scheduleId: s.id,
                            summary: (s as any).summary,
                            type: EScheduleTypes.Report,
                            userId: item.userId,
                        });
                    });
                });

                _.forEach(props.forecasts(), (item) => {
                    scheduleObj.push({
                        accessLevel: 3,
                        accessLevelName: tabPermissionLevels[3],
                        destinations: item.schedule.destinations,
                        dsiId: null,
                        id: item.schedule.id,
                        name: item.schedule.options.groups[0],
                        schedule: item.schedule,
                        scheduleId: item.schedule.id,
                        summary: item.schedule.summary,
                        type: EScheduleTypes.Forecast,
                        userId: item.schedule.userId,
                    });
                });

                _.forEach(props.scorecards(), (item) => {
                    _.forEach(item.schedules, (s) => {
                        scheduleObj.push({
                            accessLevel: item.accessLevel,
                            accessLevelName: tabPermissionLevels[item.accessLevel],
                            destinations: !_.isEmpty(s.individualScorecardEmail) ? "Individual Agents" : s.destinations,
                            dsiId: null,
                            id: item.id,
                            name: item.scorecardContent.name,
                            schedule: s,
                            scheduleId: s.id,
                            summary: s.scheduleSummary,
                            type: EScheduleTypes.Scorecard,
                            userId: item.userId,
                        });
                    });
                });

                return _.chain(scheduleObj)
                    .groupBy((rep) => rep.userId)
                    .map((schedules, userId) => {
                        const user = _.find(users, (u) => u.userId === Number(userId)) || missingUser;

                        return {
                            userId: user.userId,
                            emailAddress: ko.unwrap(user.emailAddress),
                            userName: ko.unwrap(user.name),
                            schedules: _.map(schedules, (s) => {
                                const destinations = _.uniq(
                                    (s.destinations as string).split(","),false, Utils.stringTrim);

                                return {
                                    accessLevel: s.accessLevel,
                                    accessLevelName: tabPermissionLevels[s.accessLevel],
                                    destinations,
                                    dsiId: s.dsiId || null,
                                    id: s.id,
                                    name: s.name || "(unknown)",
                                    schedule: s.schedule,
                                    scheduleId: s.scheduleId,
                                    summary: s.summary,
                                    type: s.type || "(unknown)",
                                    userId: s.userId,
                                };
                            }),
                        };
                    })
                    .filter((u) => {
                        const email = ko.unwrap(u.emailAddress);

                        if (!this.filter()) {
                            return true;
                        }
                        return (u.userName + " " + email)
                            .toLowerCase()
                            .indexOf(this.filter().toLowerCase()) !== -1;
                    })
                    .sortBy("emailAddress")
                    .value();
            });
        }

        public createEventHandlers(props: ISchedulesManagementProps) {
            this.events.onScheduleEntryClick = (data: IScheduleBR | ISchedule) => {
                let entity: BRIDs.IReportSaved | BDIs.IDashboardTab | BIs.ISystemReviewEntity | BISIs.IScorecard =
                    {} as any;
                let name: string = "";

                const scheduleToEdit = (data as ISchedule).scheduleId !== void 0 ?
                    data as ISchedule :
                    (data as IScheduleBR).schedule;
                const scheduleType = scheduleToEdit.type.toLowerCase() as BEs.DataPerspective;

                if (scheduleType === BEs.DataPerspective.Dashboard) {
                    entity = _.find(ko.utils.unwrapObservable(props.dashboards),
                        (d) => _.findIndex(d.schedules, { Id: scheduleToEdit.scheduleId }) !== -1);
                    name = (entity as BDIs.IDashboardTab).tabContent.name;
                } else if (scheduleType === BEs.DataPerspective.Report) {
                    entity = _.find(ko.utils.unwrapObservable(props.reports),
                        (d) => _.findIndex(d.schedules, { id: scheduleToEdit.scheduleId }) !== -1) as any;
                    name = (entity as any).templateContent.name;
                } else if (scheduleType === BEs.DataPerspective.Forecast) {
                    return this.openForecastingSchedule(scheduleToEdit.schedule as BIs.IForecastSchedule);
                } else if (scheduleType === BEs.DataPerspective.Scorecard) {
                    entity = _.find(ko.utils.unwrapObservable(props.scorecards),
                        (d) => _.findIndex(d.schedules, { id: scheduleToEdit.scheduleId }) !== -1) as any;
                    name = (entity as BISIs.IScorecard).name;
                }

                const emailOptions = new BVs.EmailOptionsDialog({
                    dataPerspective: scheduleType,
                    entity,
                    hideSendingOptions: true,
                    dsi: data.dsiId !== null ? Utils.DSI.findById(data.dsiId) : void 0
                });

                const schedule = _.find(emailOptions.schedules(), (s) => s.schedule.id === scheduleToEdit.scheduleId)!
                    .schedule;
                let parameters: any[] | undefined;

                if (schedule.parameters) {
                    parameters = schedule.parameters
                        .map((parameter: any) => {
                            if (!parameter.defaultFilters && parameter.hasOwnProperty("dimensionIndex")) {
                                return Utils.ReportHelpers.convertFilterToParameter(
                                    parameter,
                                    Utils.DSI.findById(data.dsiId!)!
                                );
                            }

                            return parameter;
                        });
                }

                const emailDialog = new BVs.EmailDialog({
                    dataPerspective: emailOptions.dataPerspective,
                    entityName: name,
                    onCancel: _.noop,
                    onClose: _.noop,
                    onSave: (s) => {
                        const toSave = s.toJSON();
                        (toSave as any).keepOwner = true;
                        return this.saveSchedule(data, toSave);
                    },
                    parameters: emailOptions._getParameters(parameters),
                    schedule
                });

                emailDialog.open();
            };

            this.events.onScheduleTakeOwnershipClick = (data: ISchedule) => {
                new BVs.TransferOwnershipDialog({
                    dataPerspective: data.type.toLowerCase() as BEs.DataPerspective,
                    dialogTitle: "Transfer Schedule",
                    excluseUserId: data.userId,
                    onCancel: _.noop,
                    onTransfer: (userId) => {
                        const user = _.find(props.users(), (u) => u.userId === userId);

                        return this.transferOwnership(data, userId, ko.unwrap(user!.name));
                    },
                    reportId: data.id,
                }).open();
            };

            this.events.onScheduleEntryDeleteClick = (data: IScheduleBR | ISchedule) => {
                let destinations: string[];
                let dialog: Brightmetrics.BasicDialog2;
                const waiting = ko.observable(false);
                const scheduleToEdit = (data as ISchedule).scheduleId !== void 0 ?
                    data as ISchedule : (data as IScheduleBR).schedule;

                if (Array.isArray(scheduleToEdit.destinations)) {
                    destinations = scheduleToEdit.destinations;
                } else {
                    destinations = _.invoke(scheduleToEdit.destinations.split(","), "trim");
                }

                if (this.view() === "schedulesbyuser" || destinations.length === 1) {
                    dialog = new BasicDialog2({
                        buttonLabels: "CONFIRM",
                        buttonClasses: ["c-btn--dialog-primary-dangerous"],
                        content: "Are you sure you want to delete this schedule entry?",
                        isLoading: waiting,
                        title: "Delete Schedule Entry"
                    });
                    dialog.open();
                    dialog.promise.then((label) => {
                            if (label === "CONFIRM") {
                                waiting(true);
                                this.requestRemoveSchedule(scheduleToEdit)
                                    .then(() => {
                                            waiting(false);
                                        });
                            }
                        });
                } else {
                    dialog = new BasicDialog2({
                        buttonLabels: ["DELETE ENTIRE SCHEDULE", "REMOVE SELECTED RECIPIENTS"],
                        buttonClasses: ["c-btn--dialog-secondary-dangerous", "c-btn--dialog-primary-dangerous"],
                        content: this.multipleDestinationsContent(destinations, (data as IScheduleBR).emailAddress),
                        dialogExtraClasses: "c-basic-dialog-2-800",
                        isLoading: waiting,
                        title: "Delete Schedule Entry"
                    });
                    dialog.open();
                    dialog.promise.then((label) => {
                            let $request;

                            if (label === "DELETE ENTIRE SCHEDULE") {
                                waiting(true);
                                $request = this.requestRemoveSchedule(scheduleToEdit)
                                    .then(() => waiting(false));
                            } else if (label === "REMOVE SELECTED RECIPIENTS") {
                                const $selected = $(".c-basic-dialog-2").find("input[type='checkbox']:checked");
                                const toRemove = _.map($selected, (s: HTMLInputElement) => { return s.value; });

                                if (toRemove.length === 0) {
                                    waiting(false);
                                    return;
                                }
                                const newDestinations = _.difference(destinations, toRemove);

                                waiting(true);
                                if (newDestinations.length === 0) {
                                    $request = this.requestRemoveSchedule(scheduleToEdit);
                                } else {
                                    if (scheduleToEdit.type.toLowerCase() === BEs.DataPerspective.Dashboard) {
                                        (scheduleToEdit.schedule as BIs.IDashboardSchedule).Destinations =
                                            newDestinations.join(", ");
                                    } else if (scheduleToEdit.type.toLowerCase() === BEs.DataPerspective.Report) {
                                        (scheduleToEdit.schedule as BIs.IReportSchedule).destinations =
                                            newDestinations.join(", ");
                                    } else if (scheduleToEdit.type.toLowerCase() === BEs.DataPerspective.Forecast) {
                                        (scheduleToEdit.schedule as BIs.IForecastSchedule).destinations =
                                            newDestinations.join(", ");
                                    }
                                    $request = this.saveSchedule(data, scheduleToEdit.schedule);
                                }
                                $request.then(() => waiting(false));
                            }
                        }
                    );
                }
            };

            this.events.onFilterClearClick = props.onFilterClearClick;
        }

        public openForecastingSchedule(schedule: BIs.IForecastSchedule) {
            if (_.keys(this.availableGroupsByDSGID).length === 0) {
                this.availableGroupsByDSGID = Utils.loadAvailableGroupsByDataSourceGroup();
            }

            new Brightmetrics.Insights.ViewModels.ScheduleDialog({
                addOrUpdateSchedule: (updatedSchedule) => {
                    const entity = _.find(ko.utils.unwrapObservable(this.forecasts),
                        (d) => d.schedule.id === schedule.id);

                    if (entity) {
                        this.forecasts.replace(entity, { schedule: updatedSchedule });
                    }
                },
                availableDataSourceGroups: this.availableDataSourceGroups,
                availableGroupsByDSGID: this.availableGroupsByDSGID,
                isRunOnce: false,
                schedule,
                keepUserId: true,
            }).open();
        }

        public saveSchedule(data: IScheduleBR | ISchedule, toSend: any) {
            const scheduleToEdit = (data as ISchedule).scheduleId !== void 0 ?
                    data as ISchedule : (data as IScheduleBR).schedule;
            const scheduleType = scheduleToEdit.type.toLowerCase();
            let restEndpoint = "";
            let entity: any;
            let name = "";

            if (scheduleType === BEs.DataPerspective.Dashboard) {
                entity = _.find(ko.utils.unwrapObservable(this.dashboards),
                    (d) => _.findIndex(d.schedules, { Id: scheduleToEdit.scheduleId }) !== -1);
                name = entity.tabContent.name;
            } else if (scheduleType === BEs.DataPerspective.Report) {
                entity = _.find(ko.utils.unwrapObservable(this.reports),
                    (d) => _.findIndex(d.schedules, { id: scheduleToEdit.scheduleId }) !== -1);
                name = entity.templateContent.name;
            } else if (scheduleType === BEs.DataPerspective.Forecast) {
                entity = _.find(ko.utils.unwrapObservable(this.forecasts),
                    (d)=>  d.schedule.id === scheduleToEdit.scheduleId);
                name = "Forecast";
            }

            if (scheduleToEdit.type.toLowerCase() === BEs.DataPerspective.Dashboard) {
                restEndpoint = "/Companies/" + defCompanyId + "/DashboardTabs/" + entity.tabId + "/Schedules";

                if (toSend.Id !== 0) {
                    restEndpoint = restEndpoint + "/" + toSend.Id;
                }

                _.extend(toSend, {
                    TabId: entity.tabId
                });
            } else if (scheduleType === BEs.DataPerspective.Report) {
                restEndpoint = "/ReportSchedules";

                if (toSend.id !== 0) {
                    restEndpoint += "/" + toSend.id;
                }

                toSend.reportTemplateId = toSend.id;
            } else if (scheduleType === BEs.DataPerspective.Forecast) {
                restEndpoint = "/Companies/" + defCompanyId + "/ForecastReportSchedules";

                if (toSend.id !== 0) {
                    restEndpoint += "/" + toSend.id;
                }
            }

            return Utils.ajaxRequest(restEndpoint, toSend).then(
                (response: any) => {
                    let idx: number;

                    if (scheduleType === BEs.DataPerspective.Dashboard) {
                        idx = _.findIndex(entity.schedules, (s: BIs.IDashboardSchedule) => s.Id === response.Id);

                        entity.schedules[idx] = response;
                        this.dashboards.valueHasMutated!();
                    } else if (scheduleType === BEs.DataPerspective.Report) {
                        idx = _.findIndex(entity.schedules, (s: BIs.IReportSchedule) => s.id === response.schedule.id);

                        entity.schedules[idx] = response.schedule;
                        this.reports.valueHasMutated!();
                    } else if (scheduleType === BEs.DataPerspective.Forecast) {
                        this.forecasts.valueHasMutated!();
                    }

                    Utils.notifyUser(
                        name + " Schedule was saved.",
                        ["success"]);
                },
                () => {
                    Utils.notifyUser(
                        name + " Schedule could not be saved.",
                        ["error"]);
                });
        }

        public transferOwnership(data: any, userId: number, userName: string) {
            let url = "";
            const action = { TransferOwnerShipTo: userId, asAdmin: true };

            if (data.type.toLowerCase() === BEs.DataPerspective.Report) {
                url = "/ReportSchedules/" + data.schedule.id;
            } else if (data.type.toLowerCase() === BEs.DataPerspective.Dashboard) {
                url = "/Companies/" + defCompanyId + "/DashboardTabs/" + data.id + "/Schedules/" + data.scheduleId;
            } else if (data.type.toLowerCase() === BEs.DataPerspective.Forecast) {
                url = "/Companies/" + defCompanyId + "/ForecastReportSchedules/" + data.schedule.id;
            }

            return Utils.ajaxRequest(url, action).then(
                () => {
                    Utils.notifyUser(
                        data.type + " " + data.name + " Schedule ownership was successfully transferred to " + userName,
                        ["success"]);

                    this.transferOwnershipTo(data, userId);
                    this.removeSchedule(data);
                },
                (error) => {
                    Utils.notifyUser(
                        data.type + " " + data.name + " Schedule ownership was not transferred.",
                        ["error"]);

                    return error;
                });
        }

        public transferOwnershipTo (data: any, userId: number) {
            let myReport: any;
            let replaceWith: any;

            if (data.type.toLowerCase() === BEs.DataPerspective.Report) {
                myReport = _.find(this.reports(), (arr) => arr.userId === userId && arr.templateId === data.id);

                const addReport = !Boolean(myReport);
                if (addReport) {
                    myReport = _.find(this.reports(),
                        (arr) => arr.userId === data.userId && arr.templateId === data.id);
                }
                replaceWith = $.extend(true, {}, myReport);

                if (!addReport) {
                    replaceWith.schedules.push(data.schedule);
                    this.reports.replace(myReport, replaceWith);
                } else {
                    replaceWith.accessLevel = 1;
                    replaceWith.userId = userId;
                    this.reports.push(replaceWith);
                }
            } else if (data.type.toLowerCase() === BEs.DataPerspective.Dashboard) {
                 const myDashboard = _.find(this.dashboards(),
                    (arr) => arr.userId === userId && arr.tabId === data.id);

                if (myDashboard) {
                    replaceWith = $.extend(true, {}, myDashboard);
                    replaceWith.schedules.push(data.schedule);
                    this.dashboards.replace(myDashboard, replaceWith);
                }
            } else {
                const schedule = _.find(this.forecasts(),
                    (arr) => arr.schedule.userId === data.userId && arr.schedule.id === data.id);
                if (schedule) {
                    replaceWith = $.extend(true, {}, schedule);
                    replaceWith.schedule.userId = userId;
                    this.forecasts.replace(schedule, replaceWith);
                }
            }
        }

        public requestRemoveSchedule(scheduleToEdit: ISchedule) {
            let entity: any;
            let url = "";
            const scheduleType = scheduleToEdit.type.toLowerCase();
            const scheduleId = scheduleToEdit.scheduleId;

            if (scheduleType === BEs.DataPerspective.Dashboard) {
                entity = _.find(ko.utils.unwrapObservable(this.dashboards),
                    (d) => _.findIndex(d.schedules, { Id: scheduleToEdit.scheduleId }) !== -1);
            } else if (scheduleType === BEs.DataPerspective.Report) {
                entity = _.find(ko.utils.unwrapObservable(this.reports),
                    (d) => _.findIndex(d.schedules, { id: scheduleToEdit.scheduleId }) !== -1);
            } else if (scheduleType === BEs.DataPerspective.Forecast) {
                entity = _.find(ko.utils.unwrapObservable(this.forecasts),
                    (d) => d.schedule.id === scheduleToEdit.scheduleId);
            } else if (scheduleType === BEs.DataPerspective.Scorecard) {
                entity = _.find(ko.utils.unwrapObservable(this.scorecards),
                    (d) => _.findIndex(d.schedules, { id: scheduleToEdit.scheduleId }) !== -1);
            }

            if (scheduleType === BEs.DataPerspective.Dashboard) {
                url = "/Companies/" + defCompanyId + "/DashboardTabs/" + scheduleToEdit.id + "/Schedules/" + scheduleId;
            } else if (scheduleType === BEs.DataPerspective.Report) {
                url = "/ReportSchedules/" + scheduleId;
            } else if (scheduleType === BEs.DataPerspective.Forecast) {
                url = "/Companies/" + defCompanyId + "/ForecastReportSchedules/" + scheduleId;
            } else if (scheduleType === BEs.DataPerspective.Scorecard) {
                url = "/Companies/" + defCompanyId + "/Scorecards/" + entity.id + "/Schedules/" + scheduleId;
            }

            return Utils.ajaxRequest(url, {
                _realMethod: "DELETE"
            }).then((response) => {
                    let idx: number;
                    let name = "";

                    if (scheduleType === BEs.DataPerspective.Dashboard) {
                        idx = _.findIndex(entity.schedules, (s: BIs.IDashboardSchedule) => s.Id === scheduleId);
                        entity.schedules.splice(idx, 1);
                        name = entity.tabContent.name;
                        this.dashboards.valueHasMutated!();
                    } else if (scheduleType === BEs.DataPerspective.Report) {
                        idx = _.findIndex(entity.schedules, (s: BIs.IReportSchedule) => s.id === scheduleId);
                        entity.schedules.splice(idx, 1);
                        name = entity.templateContent.name;
                        this.reports.valueHasMutated!();
                    }
                    else if (scheduleType === BEs.DataPerspective.Forecast) {
                        idx = _.findIndex(this.forecasts(), (s) => s.schedule.id === scheduleId);

                        this.forecasts().splice(idx, 1);
                        name = "Forecast";
                        this.forecasts.valueHasMutated!();
                    } else if (scheduleType === BEs.DataPerspective.Scorecard) {
                        idx = _.findIndex(entity.schedules, (s: BISIs.IScorecardSchedule) => s.id === scheduleId);

                        entity.schedules.splice(idx, 1);
                        name = entity.scorecardContent.name;
                        this.scorecards.valueHasMutated!();
                    }

                    Utils.notifyUser(
                        name + " Schedule was deleted.",
                        ["success"]);

                    return response;
                },
                (err) => {
                    Utils.notifyUser(
                        name + " Schedule could not be deleted.",
                        ["error"]);

                    return err;
                });
        }

        public removeSchedule(data: any) {
            let toReplace: any;
            let replaceWith: any;
            let idx: number;

            if (data.type.toLowerCase() === BEs.DataPerspective.Report) {
                toReplace = _.find(this.reports(), (arr) => arr.userId === data.userId && arr.templateId === data.id);

                if (toReplace) {
                    replaceWith = $.extend(true, {}, toReplace);
                    idx = _.findIndex(replaceWith.schedules, (s: any) => s.id === data.schedule.id);
                    replaceWith.schedules.splice(idx, 1);
                    this.reports.replace(toReplace, replaceWith);
                }
            } else if (data.type.toLowerCase() === BEs.DataPerspective.Dashboard) {
                toReplace = _.find(this.dashboards(), (arr) => arr.userId === data.userId && arr.tabId === data.id);
                if (toReplace) {
                    replaceWith = $.extend(true, {}, toReplace);
                    idx = _.findIndex(replaceWith.schedules, (s: any) => s.id === data.schedule.id);
                    replaceWith.schedules.splice(idx, 1);
                    this.dashboards.replace(toReplace, replaceWith);
                }
            } else {
                this.forecasts.remove((s: any) => s.schedule.userId === data.userId && s.schedule.id === data.id);
            }
        }

        public multipleDestinationsContent(destinations: string[], clicked: string) {
            return "<div class='schedule-recipient-delete-dlg'>" +
                "<p>There are multiple recipients on this schedule entry. You may either delete the schedule entry or select all of the recipients you would like to remove.</p>" +
                "<br /><span>Recipients:</span>" +
                "<table class='zebra' style='width: 100%; margin-top: 10px'>" +
                "<tbody>" +
                _.map(destinations, (dest) => {
                    const checked = dest === clicked ? " checked='checked'" : "";
                    return ("<tr>" +
                        "<td style='width: 40px'>" +
                        "<label class='c-checkbox'>" +
                        "<input type='checkbox' value='" + dest + "' " + checked + " class='c-checkbox__actual' />" +
                        "<span class='c-checkbox__display'></span></label></td>" +
                        "<td>" + dest + "</td>" +
                        "</tr>");
                }).join("") +
                "</tbody>" +
                "</table>" +
                "</div>";
        }
    }
}
