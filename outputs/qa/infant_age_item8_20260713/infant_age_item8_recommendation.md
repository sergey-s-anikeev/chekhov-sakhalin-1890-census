# Item 8 precise infant/young-child age proposal

## Finding

The leading age phrase can be extracted deterministically from 307 `comments` values. The current `age` field remains completed years. No comment text is changed in this proposal.

## Recommended representation

Use `age_months` as the primary numeric precision field for expressions stated in months or in years plus months. Months are the dominant source unit and total completed months preserve the existing completed-year interpretation (`age == age_months // 12`). Do not convert weeks or days into fractional months because that would add an unsupported conversion assumption.

Also retain `age_text_raw` as the exact extracted source phrase. For the 17 explicit week/day expressions, leave `age_months` blank and preserve their exact wording in `age_text_raw`. Separate `age_weeks` and `age_days` columns are not recommended for the final minimal schema because the exact submonth values are already retained and the fields would be populated in only 15 and two records respectively.

## Comment handling

Copy only the leading age phrase into `age_text_raw`. Preserve `comments` unchanged during Item 8. `comments_residual_preview` shows what would remain if the age phrase were removed in a later, separately approved comment-cleanup item; it is evidence only and is not a proposed edit now.
