namespace Brightmetrics.Utils {
    export namespace TimeKeeper {
        interface IFallbackDateTimeOffsetResponse {
            data: {
                milliseconds: number;
                seconds: number;
            };
        }

        /**
         * IE ONLY
         * -------
         * Stick the tz offset result in this cache if we have to look it up.
         * That way we only need to make the request once per tz.
         */
        const fallbackDateTimeOffsetCache = {} as {
            [timeZoneId: string]: number;
        };

        /**
         * Get tz name in IANA format. `Intl.DateTimeFormat`'s `timeZone`
         * option prefers that format.
         */
        function getIANATimeZoneName(timeZoneId: string): string | undefined {
            const values = _.find(windowsZones.tzmapping, (m) => m[0] === timeZoneId);

            if (!values) {
                return undefined;
            }

            const value = _.find(values[1], (z) => {
                return _.any(z, (e) => e === true);
            });

            if (!value) {
                return undefined;
            }

            return value[1] as string;
        }

        /**
         * Get `Intl.DateTimeFormat` object configured for a specific tz.
         */
        function getDateTimeFormatterForTimezone(
            timeZoneId: string,
            formattingOptions?: Intl.DateTimeFormatOptions)
            : Intl.DateTimeFormat {
            const formatter = new Intl.DateTimeFormat(undefined, formattingOptions);

            if (!timeZoneId) {
                return formatter;
            }

            if (useIETimeZoneFallback) {
                const tzData = _.find(supportedTimeZones, (z) => z.id === timeZoneId);

                if (tzData) {

                    // Ugh. In IE there's no simple way to determine offset when
                    // daylight saving is in effect. So we go to the server.

                    return {
                        format(date: Date) {
                            if (!fallbackDateTimeOffsetCache.hasOwnProperty(timeZoneId)) {
                                $.get(`/ClientUtils.ashx/DateTime/GetOffset?tz=${encodeURIComponent(timeZoneId)}`)
                                    .then((response: IFallbackDateTimeOffsetResponse) => {
                                        fallbackDateTimeOffsetCache[timeZoneId] = response.data.milliseconds;
                                    });
                            } else {

                                // Convert the local date to UTC, then offset it.
                                date = new Date(date.getTime() +
                                    (date.getTimezoneOffset() * 60000) +
                                    fallbackDateTimeOffsetCache[timeZoneId]);
                            }

                            return date.toLocaleTimeString(undefined, formattingOptions);
                        },
                        resolvedOptions() {
                            throw new Error("Not Implemented");
                        }
                    };
                }

                return formatter;
            }

            const timeZone = getIANATimeZoneName(timeZoneId);

            if (timeZone) {
                return new Intl.DateTimeFormat(undefined, {
                    timeZone,
                    ...formattingOptions
                });
            }

            return formatter;
        }

        let intervalHandle = -1;
        const now = ko.observable<Date>();
        const formatterDefaults = {
            hour: "numeric",
            minute: "numeric",
        } as Intl.DateTimeFormatOptions;

        function start() {
            now(new Date());
            intervalHandle = setInterval(() => now(new Date()), 1000);
        }

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

    export const stringTrim = $.trim;

    // tslint:disable-next-line:max-line-length
    export const emailAddressRegex = /^[a-zA-Z0-9!#$%&'*+\-\/=?\^_`{|}~](\.?[a-zA-Z0-9!#$%&'*+\-\/=?\^_`{|}~])*@([a-zA-Z0-9][a-zA-Z0-9\-]*\.)+[a-zA-Z]{2,}$/;
    export const validHostnameRx = /^([a-zA-Z0-9][a-zA-Z0-9\-]*\.)+[a-zA-Z]{2,4}$/;
}
