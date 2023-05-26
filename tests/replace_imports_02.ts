/// <reference path="../viewmodel.ts" />

namespace Brightmetrics.ViewModels {
    import BCs = Brightmetrics.Classes;
    import BIs = Brightmetrics.Interfaces;
    import BEs = Brightmetrics.Enums;
    import BDIs = Brightmetrics.Dashboard.Interfaces;
    import BRIs = Brightmetrics.Reports.Interfaces;
    import BRIDs = Brightmetrics.Reports.Interfaces.DTOs;
    import BISIs = Brightmetrics.Insights.Scorecards.Interfaces;
    import Utils = Brightmetrics.Utils;

    declare var defCompanyId: number;

    type ReportOrDashboard = BRIDs.IReportSaved | BDIs.IDashboardTab |
        BIs.ISystemReviewEntity | BISIs.IScorecard;

    function handleOverflow(words: string[], max: number) {
        if (words.length > max) {
            words = words.slice(0, max).concat(`and ${words.slice(max).length} more`);
        }

        return words;
    }

    interface IScheduleEntryProps {
        dataPerspective: BEs.DataPerspective;
        schedule: BCs.ScheduleEntry;
        entity: ReportOrDashboard;
        hideDuplicateButton?: boolean;
        onDelete: (s: BCs.ScheduleEntry) => Promise<any>;
        onDuplicate: (s: BCs.ScheduleEntry) => void;
        onEdit: (s: BCs.ScheduleEntry) => void;
        onSendNow: (s: BCs.ScheduleEntry) => void;
        onTransferOwnership: (s: BCs.ScheduleEntry) => void;
    }

    export class ScheduleEntry extends ViewModel {
        private _dataPerspective: BEs.DataPerspective;
        private _entity: ReportOrDashboard;

        public schedule: BCs.ScheduleEntry;
        public subject: string;
        public destinations: string;
        public destinationsOverflowed: number;
        public destinationsTooltip: string;
        public summary: string;
        public isLoading: KnockoutObservable<boolean>;
        public individualScorecardEmail: boolean;
        public hideDuplicateButton?: boolean;

        constructor(props: IScheduleEntryProps) {
            super(props);
        }

        private _assignUIDestinations() {
            const dests = _.uniq(this.schedule.destinations);

            if (dests.length > 1) {
                this.destinations = dests.slice(0, 1).join(", ");
                this.destinationsOverflowed = dests.slice(1).length;
                this.destinationsTooltip = dests.slice(1).join(", ");
            } else {
                this.destinations = dests.join(", ");
                this.destinationsOverflowed = 0;
                this.destinationsTooltip = "";
            }
        }

        private _getUISummary() {
            const summary = this.schedule.scheduleSummary;
            let breakWords: string;
            const breakWords1 = " every ";
            const breakWords2 = " on the ";
            let breakIndex: number;
            const breakIndex1 = summary.indexOf(breakWords1);
            const breakIndex2 = summary.indexOf(breakWords2);
            let wordsBeforeBreak: string[];
            let wordsAfterBreak: string[];

            if (breakIndex1 !== -1) {
                breakIndex = breakIndex1;
                breakWords = breakWords1;
            } else if (breakIndex2 !== -1) {
                breakIndex = breakIndex2;
                breakWords = breakWords2;
            } else {
                // Maybe there is a schedule summary without the break words..?
                return summary;
            }

            wordsBeforeBreak = handleOverflow(summary.substr(0, breakIndex).split(", "), 3);
            wordsAfterBreak = handleOverflow(summary.substr(breakIndex + breakWords.length).split(", "), 3);

            return wordsBeforeBreak.length > wordsAfterBreak.length ?
                (wordsBeforeBreak.join(", ") + "<br />" + breakWords + wordsAfterBreak.join(", ")) :
                (wordsBeforeBreak.join(", ") + breakWords + "<br />" + wordsAfterBreak.join(", "));
        }

        private _getUISubject() {
            return this.schedule.customSubject || this.schedule.defaultSubject;
        }

        private _createMoreVert(position: JQuery.Coordinates, props: IScheduleEntryProps) {
            const items: BIs.IMoreVertItems[] = [
                {
                    click: () => props.onSendNow(this.schedule),
                    icon: null,
                    text: "SEND NOW",
                },
                {
                    click: () => props.onTransferOwnership(this.schedule),
                    icon: null,
                    text: "TRANSFER OWNERSHIP",
                },
                {
                    click: _.bind(this.events.onDeleteClick, this),
                    icon: null,
                    text: "DELETE",
                }
            ];
            if (!(this.hideDuplicateButton && this.hideDuplicateButton === true)) {
                items.push({
                    click: () => props.onDuplicate(this.schedule),
                    icon: null,
                    text: "DUPLICATE",
                })
            }
            let moreVert = Utils.moreVert(items, {
                onRemove: () => {
                    moreVert = null;
                },
                position,
                showInDialog: true
            }) as any;
        }

        public initialize(props: IScheduleEntryProps) {
            this._dataPerspective = props.dataPerspective;
            this._entity = props.entity;
            this.schedule = props.schedule;
            this._assignUIDestinations();
            this.subject = this._getUISubject();
            this.summary = this._getUISummary();
            this.isLoading = ko.observable(false);
            this.hideDuplicateButton = props.hideDuplicateButton;
            this.individualScorecardEmail = Boolean(props.schedule.individualScorecardEmail);
        }

        public createEventHandlers(props: IScheduleEntryProps) {
            this.events.onEditClick = () => {
                props.onEdit(this.schedule);
            };

            this.events.onDeleteClick = () => {
                const always = () => { this.isLoading(false); };

                Utils.basicConfirm(
                    "Are you sure you want to delete this scheduled email?",
                    "Delete Schedule",
                    "Delete",
                    { isDangerous: true })
                    .then(() => {
                        this.isLoading(true);

                        props.onDelete(this.schedule).then(always, always);
                    });
            };

            this.events.onMoreVertClick = (ignore: unknown, event: JQuery.Event) => {
                this._createMoreVert({
                    left: event.pageX,
                    top: event.pageY
                }, props);
            };
        }
    }
}
