-- Test métier : une ligne non éligible ne doit jamais porter de base positive.
-- Sans ce contrôle, une ligne annulée ou non facturée pourrait créer du revenu.

select
    order_id,
    line_id,
    base_ht,
    est_eligible_vente

from {{ ref('stg_order_lines') }}

where not est_eligible_vente
  and base_ht <> 0
