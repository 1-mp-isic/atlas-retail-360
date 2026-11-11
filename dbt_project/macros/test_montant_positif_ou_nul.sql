{#
    Test générique métier : un montant monétaire ne doit jamais être négatif.
    S'applique aux bases, remises et remboursements, qui sont des montants
    positifs par contrat. À ne PAS appliquer au CA net, qui peut être négatif
    sur une période à forts retours (section 08).
#}

{% test montant_positif_ou_nul(model, column_name) %}

    select {{ column_name }}
    from {{ model }}
    where {{ column_name }} < 0

{% endtest %}
