# NOTES

- I don't think we need to format each file. They are mostly formatted, aside
  from perhaps line-ending and whitespace inconsistencies

# PRE

- Need to move certain things around so they are semantically correct
    - Any file paths that don't line up with the namespace path
    - IAlert
    - etc
- Need to move all sub-namespaces to their own file
    - ReportHelpers, Dates, other "export namespace" declarations
    - Otherwise, the scraping logic gets more complicated
- Remove export namespace in Reports base (Needs to be done before step 3
  below)
    - See what broke to determine next step

# TRANSFORM

1. Remove stupid comments and stuff
    - Reference tags
    - JSHint
2. Unindent all files that have a top-level namespace
3. Replace all namespace imports
    - Make sure things that reference them (in-file) are replaced 
4. Gather all exports
    - Make sure to grab their context, and whatever other details
5. Replace all export references w/ fully qualified
    1. Ignore it if it's an export
    2. If on the same namespace, then replace
        ```
        "Report" in "Brightmetrics.Reports.ViewModels[.Editor]"
        "weekdayNames" in "Brightmetrics.Constants"
        ```
    3. If more than one symbol in match, then replace it

# POST
