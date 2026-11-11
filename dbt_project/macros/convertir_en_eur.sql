{#
    Convertit un montant vers EUR selon la règle de la section 07 :
      - taux à la date locale de facture ;
      - à défaut, le taux disponible le plus récent ANTÉRIEUR ;
      - recul maximum de fx_lookback_days jours calendaires (7 par défaut) ;
      - aucun taux futur n'est accepté ;
      - EUR vaut 1, l'absence de taux EUR est normale.

    Au-delà de la fenêtre, la macro renvoie NULL : le montant est alors
    « non valorisé » et la certification du périmètre est bloquée en aval.
    La macro ne décide pas de la quarantaine, elle signale seulement l'absence.
#}

{% macro convertir_en_eur(montant, devise, date_locale, alias_taux='fx') %}
    case
        when {{ devise }} = 'EUR' then {{ montant }}
        when {{ alias_taux }}.eur_per_unit is null then cast(null as decimal(18, 4))
        else {{ montant }} * {{ alias_taux }}.eur_per_unit
    end
{% endmacro %}


{#
    Jointure du taux applicable. À utiliser en LEFT JOIN LATERAL ou via une
    table de taux densifiée, selon la stratégie retenue en S7.
#}
{% macro clause_taux_applicable(devise, date_locale, fenetre=none) %}
    {%- set fenetre = fenetre if fenetre is not none else var('fx_lookback_days') -%}
    fx.currency = {{ devise }}
    and fx.rate_date <= {{ date_locale }}
    and fx.rate_date >= date_sub({{ date_locale }}, {{ fenetre }})
{% endmacro %}
