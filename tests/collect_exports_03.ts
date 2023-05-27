namespace Brightmetrics.Admin.Interfaces{
    export interface ILinkSettings{
        name: string;
        tabId: string;
        links?: ILinkEntry[];
        dataVersion: Brightmetrics.Dashboard.Enums.DataVersion;
    }

    export interface ILinkEntry{
        id: string;
        companyId: number;
        credentials: string;
        isLegacyToken: boolean;
        dashboardTab: string;
        description: string;
        link: string;
        whitelistedIPAddresses: ILinkIpAddress[];
        theme: Brightmetrics.Enums.Theme;
    }

    export interface ILinkIpAddress{
        ipAddress: string;
        description: string;
    }
}
