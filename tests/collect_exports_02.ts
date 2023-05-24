/// <reference path="../../../ViewModels/pill.ts" />
namespace Brightmetrics.Admin.VoiceAnalytics.ViewModels {
    import MSVs = Brightmetrics.MultipleSelect.ViewModels;
    import VAIs = Brightmetrics.VoiceAnalytics.Interfaces;
    import Dialog = Brightmetrics.ViewModels.DialogViewModel;

    interface IProps<T = string | number> extends Brightmetrics.Interfaces.IPillProps<T> {
        parentDialog?: Brightmetrics.ViewModels.DialogViewModel;
        onUpdate: (values: T[]) => void;
        innerListLabel: string;
        innerListFetcher: () => Promise<Array<IKoOption<T>>>;
        presetValues?: () => T[];
        pillLabel: KnockoutComputed<string>;
    }

    export namespace SubPill {
        export type Props<T = string | number> = IProps<T>;
    }

    export class SubPill<T = string | number> extends Brightmetrics.ViewModels.Pill<T> {
        public label: KnockoutComputed<string>;

        public constructor(props: IProps<T>) {
            super(props);
        }

        private _injectTemplate() {
            if (!document.scripts.namedItem(this.templateId)) {
                const script = document.createElement("SCRIPT") as HTMLScriptElement;
                script.type = "text/html";
                script.id = this.templateId;
                script.innerHTML = `
<span class="
           c-pill
           c-pill--clickable
           u-valign-middle"
      style="
           user-select: none;
           -ms-user-select: none;
           margin: 0 3px 3px 0;"
      contenteditable="false"
      unselectable="on">
    <span class="c-pill__content">
        <span class="c-pill__text"
              data-bind="click: events.onLabelClick">
            <span data-bind="text: label"></span>
        </span>
        <span class="c-pill__icon"
              data-icon-code="cancel"
              data-bind="click: events.onRemoveClick"></span>
    </span>
</span>
`;

                document.body.appendChild(script);
            }
        }

        private _openSubDialog(props: IProps<T>) {
            const dialog: Dialog = new MSVs.MultipleSelectDialog<T>({
                listFetcher: (ignore) => props.innerListFetcher(),
                listLabels: [props.innerListLabel],
                nameForItem: props.innerListLabel,
                onUpdate: (data) => {
                    props.onUpdate(data.values.map(x => x.value));
                },
                beforeDestroy: () => {
                    if (props.parentDialog) {
                        return dialog.transitionSlide(props.parentDialog, true);
                    }
                    return Brightmetrics.Constants.resolvedDeferred;
                },
                presetValues: props.presetValues ? props.presetValues() : [],
            });

            if (props.parentDialog) {
                dialog.create();

                props.parentDialog.transitionSlide(dialog, false);
            } else {
                dialog.open();
            }
        }

        public initialize(props: IProps<T>) {
            super.initialize(props);

            this.templateId = "tag-pill-template";

            this._injectTemplate();
        }

        public initSubscriptions(props: IProps<T>) {
            this.label = props.pillLabel;
        }

        public createEventHandlers(props: IProps<T>) {
            props.onRemove = () => {
                const parentDialog = props.parentDialog as MSVs.MultipleSelectDialog<T>;
                const listItem = _.find(parentDialog.multipleSelect.selectedItems(), (item) =>
                    item.value === this.value)!;

                listItem.isChecked(false);
            };

            super.createEventHandlers(props);

            this.events.onLabelClick = () => this._openSubDialog(props);
        }
    }
}
