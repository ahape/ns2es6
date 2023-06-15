namespace Brightmetrics.Utils {
    export const stringTrim = $.trim;

    export const foo = () => {
        return 1;
    }

    export namespace TimeKeeper {
        /** For debugging, if necessary. */
        export function stop() {
            clearInterval(intervalHandle);
            intervalHandle = -1;
        }

        /**
         * Returns a `KnockoutComputed` that itself returns a locale time-
         * string for the specified tz. The computed updates every sec.
         */
        export function getNew(
            timeZone: string,
            use24HourFormat: boolean,
            showSeconds: boolean)
            : KnockoutComputed<string>
        {
            if (intervalHandle === -1) {
                start();
            }

            const formatter = getDateTimeFormatterForTimezone(timeZone, {
                ...formatterDefaults,
                hour12: !use24HourFormat,
                second: showSeconds ? "numeric" : undefined,
            });

            return ko.pureComputed(() => formatter.format(now()));
        }
    }

    export const validHostnameRx = /^([a-zA-Z0-9][a-zA-Z0-9\-]*\.)+[a-zA-Z]{2,4}$/;
}
