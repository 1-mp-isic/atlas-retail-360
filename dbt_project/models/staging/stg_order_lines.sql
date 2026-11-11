{{
  config(
    materialized = 'view',
    tags = ['silver', 'ventes']
  )
}}

-- Grain : une ligne de commande, dans son état courant.
-- Une ligne ne crée une vente que si elle est facturée, non annulée et de
-- quantité strictement positive (section 07). Le statut commercial de la
-- commande ne remplace pas la preuve de facturation.

with versions as (

    select
        order_id,
        line_id,
        product_id,
        cast(qty_ordered as int)                 as qty_ordered,
        cast(qty_invoiced as int)                as qty_invoiced,
        cast(unit_price_ht as decimal(18, 4))    as unit_price_ht,
        cast(line_discount_ht as decimal(18, 4)) as line_discount_ht,
        cast(invoice_ts as timestamp)            as invoice_ts,
        cast(is_cancelled as boolean)            as is_cancelled,
        op,
        cast(source_version as bigint)           as source_version,
        batch_id

    from {{ source('bronze', 'order_lines') }}

),

derniere_version as (

    select
        *,
        row_number() over (
            partition by order_id, line_id
            order by source_version desc
        ) as rang

    from versions

)

select
    order_id,
    line_id,
    product_id,
    qty_ordered,
    qty_invoiced,
    unit_price_ht,
    line_discount_ht,
    invoice_ts,
    is_cancelled,
    source_version,
    batch_id,
    op = 'D' as est_supprime,
    -- Base HT de la ligne avant répartition de la remise de commande.
    case
        when op = 'D' then cast(0 as decimal(18, 4))
        when is_cancelled then cast(0 as decimal(18, 4))
        when invoice_ts is null then cast(0 as decimal(18, 4))
        when qty_invoiced <= 0 then cast(0 as decimal(18, 4))
        else qty_invoiced * unit_price_ht - line_discount_ht
    end as base_ht,
    -- Éligible au revenu : les quatre conditions de la section 07 réunies.
    (op <> 'D'
        and not is_cancelled
        and invoice_ts is not null
        and qty_invoiced > 0) as est_eligible_vente

from derniere_version
where rang = 1
