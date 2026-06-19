-- Fix 1: Grant view access to authenticated users
grant select on public.dispatch_summary to authenticated;
grant select on public.dispatch_summary to anon;

-- Fix 2: Recreate view with security definer so RLS doesn't block it
drop view if exists public.dispatch_summary;

create or replace view public.dispatch_summary
with (security_invoker = false)
as
select
  count(*)                                                        as total_dispatches,
  coalesce(sum(doc_net_value), 0)                                 as total_value,
  count(*) filter (where lr_final_status = 'Delivered')           as delivered_count,
  count(*) filter (where lr_final_status in ('TBC',''))           as tbc_count,
  count(*) filter (where lr_final_status in ('In Transit','Transit')) as in_transit_count,
  count(*) filter (where doc_date >= date_trunc('month', current_date)) as this_month
from public.dispatches;

grant select on public.dispatch_summary to authenticated;
grant select on public.dispatch_summary to anon;

-- Fix 3: Also verify dispatches are readable
grant select on public.dispatches to authenticated;

-- Quick check: how many rows exist?
select count(*) as total_rows, sum(doc_net_value) as total_value from public.dispatches;
