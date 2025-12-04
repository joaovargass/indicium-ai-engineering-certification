## Page 1

&lt;img&gt;Brazilian Coat of Arms&lt;/img&gt;
MINISTÉRIO DA SAÚDE
SECRETARIA DE VIGILÂNCIA EM SAÚDE

SIVEP-Gripe
SISTEMA DE INFORMAÇÃO DA VIGILÂNCIA EPIDEMIOLÓGICA DA GRIPE
25/05/2023.

# Dicionário de Dados

*FICHA DE REGISTRO INDIVIDUAL – CASOS DE SÍNDROME RESPIRATÓRIA AGUDA GRAVE HOSPITALIZADOS*

Este documento tem como finalidade descrever as variáveis exportadas para o banco de dados em DBF.

CAMPO OBRIGATÓRIO é aquele cuja ausência de dado impossibilita a inclusão do registro no sistema.
CAMPO ESSENCIAL é aquele que, apesar de não ser obrigatório, registra dado necessário à investigação do caso ou ao cálculo de indicador epidemiológico ou operacional.
CAMPO INTERNO é aquele que apesar de não constar na ficha e não aparecer no display da tela, é preenchido automaticamente pelo sistema.
CAMPO OPCIONAL é aquele que só deve ser preenchido caso seja necessário, aparece no display da tela e consta no banco de dados.

<table>
  <thead>
    <tr>
      <th>Nome do campo</th>
      <th>Tipo</th>
      <th>Categoria</th>
      <th>Descrição</th>
      <th>Características</th>
      <th>DBF</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Nº</td>
      <td>Varchar2(12)</td>
      <td></td>
      <td>Número do registro</td>
      <td><b>Campo Interno</b><br><br>Número sequencial gerado automaticamente pelo sistema.<br><br>Utilizar o padrão:<br>320120000123<br><br>Dígito 1: caracteriza o tipo da ficha (1=SG, 2=SRAG-UTI e 3-SRAG Hospitalizado).<br><br>Dígitos 2 a 12: número sequencial gerado automaticamente pelo sistema.</td>
      <td>NU_NOTIFIC</td>
    </tr>
    <tr>
      <td>1-Data do preenchimento da ficha de notificação</td>
      <td>Date DD/MM/AAAA</td>
      <td></td>
      <td>Data de preenchimento da ficha de notificação.</td>
      <td><b>Campo Obrigatório</b><br><br>Data deve ser <= a data da digitação.</td>
      <td>DT_NOTIFIC</td>
    </tr>
    <tr>
      <td>Semana Epidemiológica do preenchimento da ficha de notificação</td>
      <td>Varchar2(6)</td>
      <td></td>
      <td>Semana Epidemiológica do preenchimento da ficha de</td>
      <td><b>Campo Interno</b><br><br>Calculado a partir da data dos Primeiros Sintomas.<br>(SS)</td>
      <td>SEM_NOT</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 1&lt;/page_number&gt;</footer>

---


## Page 2

<table>
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th></th>
      <th>notificação.</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2-Data de 1ºs sintomas</td>
      <td>Date<br>DD/MM/AAAA</td>
      <td></td>
      <td>Data de 1º sintomas do caso.</td>
      <td>Campo Obrigatório<br><br>Data deve ser <= a data da digitação e data do preenchimento da ficha de notificação</td>
      <td>DT_SIN_PRI</td>
    </tr>
    <tr>
      <td>Semana Epidemiológica dos Primeiros Sintomas</td>
      <td>Varchar2(6)</td>
      <td></td>
      <td>Semana Epidemiológica do início dos sintomas.</td>
      <td>Campo Interno<br><br>Calculado a partir da data dos Primeiros Sintomas.<br>(SS)</td>
      <td>SEM_PRI</td>
    </tr>
    <tr>
      <td>3-UF</td>
      <td>Varchar2(2)</td>
      <td>Tabela com código e siglas das UF padronizados pelo IBGE.</td>
      <td>Unidade Federativa onde está localizada a Unidade que realizou a notificação.</td>
      <td>Campo Obrigatório<br><br>Se usuário que está digitando a ficha for de nível:<br><ul><li>Unidade - o campo é preenchido automaticamente pelo sistema com a UF, município e unidade onde está cadastrado o usuário.</li><li>Municipal – o campo é preenchido automaticamente pelo sistema com a UF e município onde está cadastrado o usuário.</li><li>Estadual – o campo é preenchido automaticamente pelo sistema com a UF do usuário.</li><li>Federal - abre tabela com todas as UF que possuam unidades cadastradas no sistema.</li></ul></td>
      <td>SG_UF_NOT</td>
    </tr>
    <tr>
      <td>4-Município Código (IBGE)</td>
      <td>Varchar2 (6)</td>
      <td>Tabela com código e nomes dos Municípios padronizados pelo IBGE.</td>
      <td>Município onde está localizada a Unidade que realizou a notificação.</td>
      <td>Campo Obrigatório<br><br>Preenchendo o nome do município de notificação, o código é preenchido automaticamente, e vice-versa;<br><br>Se usuário que está digitando a ficha for de nível:<ul><li>Unidade – o campo é preenchido automaticamente pelo sistema com o Município onde está localizada a unidade de notificação.</li><li>Municipal – o campo é preenchido automaticamente pelo sistema com o município do usuário.</li><li>Estadual ou Federal – abre tabela com todos os municípios da UF selecionada no campo 3 que possuam unidades cadastradas no sistema.</li></ul></td>
      <td>ID_MUNICIP OU CO_MUN_NOT</td>
    </tr>
    <tr>
      <td>Regional de Saúde de Notificação Código (IBGE)</td>
      <td>Varchar2 (6)</td>
      <td>Tabela com código e nomes das Regionais de Saúde dos municípios de notificação padronizados pelo IBGE.</td>
      <td>Regional de Saúde onde está localizado o Município realizou a notificação.</td>
      <td>Campo Interno<br><br>Preenchendo o nome da regional de saúde de notificação, o código é preenchido automaticamente, e vice-versa;<br><br>Se usuário que está digitando a ficha for de nível:</td>
      <td>ID_REGIONA OU CO_REGIONA</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 2&lt;/page_number&gt;</footer>

---


## Page 3

<table>
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>5-Unidade de Saúde Código (CNES)</td>
      <td>Varchar2(7)</td>
      <td>Tabela com códigos CNES e nomes das Unidades cadastradas no sistema.</td>
      <td>Unidade que realizou o atendimento, coleta de amostra e registro do caso.</td>
      <td>
        <ul>
          <li><u>Unidade</u> – o campo é preenchido automaticamente pelo sistema com a Regional do Município onde está localizada a unidade de notificação.</li>
          <li><u>Municipal</u> – o campo é preenchido automaticamente pelo sistema com a regional do município do usuário.</li>
        </ul>
      </td>
      <td>ID_UNIDADE OU CO_UNI_NOT</td>
    </tr>
    <tr>
      <td>6- Tem CPF?</td>
      <td>Varchar(1)</td>
      <td>1-Sim<br>2-Não</td>
      <td>Informar se o paciente notificado dispõe de Número do Cadastro de Pessoa Física (CPF)</td>
      <td>
        <ul>
          <li><b>Campo Obrigatório</b></li>
          <li>Se usuário que está digitando a ficha for de nível:</li>
          <ul>
            <li><u>Unidade</u> - o campo é preenchido automaticamente pelo sistema.</li>
            <li><u>Municipal</u> – abre tabela apenas com as unidades do município.</li>
            <li><u>Estadual ou Federal</u> – abre tabela com as unidades do município selecionado o campo 4.</li>
          </ul>
        </ul>
      </td>
      <td>TEM_CPF</td>
    </tr>
    <tr>
      <td>7-CPF do paciente</td>
      <td>Varchar2(15)</td>
      <td>Numérico (11 dígitos)</td>
      <td>Número do Cadastro de Pessoa Física (CPF) do paciente notificado</td>
      <td>
        <ul>
          <li><b>Campo Obrigatório</b></li>
          <li>Se selecionado “Sim”, preencher campo “CPF”. Se selecionado “Não” preencher CNS. Se o paciente não dispor de CPF é obrigatório o preenchimento do CNS. No caso de pacientes raça/cor indígenas, somente o CNS é considerado como campo obrigatório.</li>
        </ul>
      </td>
      <td>NU_CPF</td>
    </tr>
    <tr>
      <td>8- Estrangeiro</td>
      <td>Varchar(1)</td>
      <td>1-Sim<br>2-Não</td>
      <td>Informar se o paciente é estrangeiro</td>
      <td>
        <ul>
          <li><b>Campo Obrigatório</b></li>
          <li>Se selecionado “Sim”, o campo CPF e CNS, deixa de ser obrigatório.</li>
        </ul>
      </td>
      <td>ESTRANG</td>
    </tr>
    <tr>
      <td>9- Cartão Nacional de Saúde (CNS)</td>
      <td>Varchar2(15)</td>
      <td>Numérico (14 dígitos)</td>
      <td>Preencher com o número do Cartão Nacional de Saúde do paciente</td>
      <td>
        <ul>
          <li><b>Campo Obrigatório</b></li>
        </ul>
      </td>
      <td>NU_CNS</td>
    </tr>
    <tr>
      <td>10-Nome</td>
      <td>Varchar2(70)</td>
      <td></td>
      <td>Nome completo do paciente (sem abreviações)</td>
      <td>
        <ul>
          <li><b>Campo Obrigatório</b></li>
        </ul>
      </td>
      <td>NM_PACIENT</td>
    </tr>
    <tr>
      <td>11-Sexo</td>
      <td>Varchar2 (1)</td>
      <td>1-Masculino</td>
      <td>Sexo do paciente.</td>
      <td>
        <ul>
          <li><b>Campo Obrigatório</b></li>
        </ul>
      </td>
      <td>CS_SEXO</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 3&lt;/page_number&gt;</footer>

---


## Page 4

<table>
  <thead>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>12-Data de nascimento</td>
      <td>Date<br>DD/MM/AAAA</td>
      <td>2-Feminino<br>9-Ignorado</td>
      <td>Data de nascimento do paciente.</td>
      <td>Campo Essencial<br><br>Data deve ser <= a data dos primeiros sintomas.</td>
      <td>DT_NASC</td>
    </tr>
    <tr>
      <td>13-(ou) Idade</td>
      <td>Varchar2(3)</td>
      <td></td>
      <td>Idade informada pelo paciente quando não se sabe a data de nascimento.<br><br>Na falta desse dado é registrada a idade aparente.</td>
      <td>Campo Obrigatório<br><br>Se digitado a data de nascimento, a idade é calculada e preenchida automaticamente pelo sistema: considerando o intervalo entre a data de nascimento e a <u>data dos primeiros sintomas</u>.<br><br>Idade deve ser <= 150.</td>
      <td>NU_IDADE_N</td>
    </tr>
    <tr>
      <td>(ou) Tipo/Idade</td>
      <td>Varchar2(1)</td>
      <td>1-Dia<br>2-Mês<br>3-Ano</td>
      <td></td>
      <td>Campo Obrigatório<br><br>Se digitado a data de nascimento, o campo Idade/Tipo é calculado e preenchido automaticamente pelo sistema: considerando o intervalo entre a data de nascimento e a <u>data dos primeiros sintomas</u>.<br><br>Se a diferença for de 0 a 30 dias, o sistema grava em Idade = (nº dias) e em Tipo = 1-Dia. Por exemplo: se Data de nascimento = 05/12/2012 e Data dos 1ºs sintomas = 11/12/2012, então Idade = 6 e Tipo = 1-Dia.<br><br>Se a diferença for de 1 a 11 meses, o sistema grava em Idade = (nº meses) e em Tipo = 2-Mês. Por exemplo: se Data de nascimento = 05/10/2012 e Data dos 1ºs sintomas = 11/12/2012, então Idade = 2 e Tipo = 2-Mês.<br><br>Se a diferença for maior ou igual a 12 meses, o sistema grava em Idade = (nº anos) e em Tipo = 3-Ano. Por exemplo: se Data de nascimento = 05/10/2011 e Data dos 1ºs sintomas = 11/12/2012, então Idade = 1 e Tipo = 3-Ano.</td>
      <td>TP_IDADE</td>
    </tr>
    <tr>
      <td>14-Gestante</td>
      <td>Varchar2(1)</td>
      <td>1-1º Trimestre<br>2-2º Trimestre<br>3-3º Trimestre<br>4-Idade Gestacional<br>Ignorada<br>5-Não<br>6-Não se aplica<br>9-Ignorado</td>
      <td>Idade gestacional da paciente.</td>
      <td>Campo Obrigatório<br><br>Se selecionado categoria 2-Feminino no campo Sexo.<br><br>Se selecionado sexo igual a <u>Masculino</u> ou a <u>idade</u> for menor ou igual a 9 anos o campo é preenchido automaticamente com 6-Não se aplica.<br><br>Se selecionado sexo igual a <u>Feminino</u> e idade for maior que 9 anos, o campo não pode ser preenchido com 6-Não se aplica.</td>
      <td>CS_GESTANT</td>
    </tr>
    <tr>
      <td>15-Raça/Cor</td>
      <td>Varchar2(2)</td>
      <td>1-Branca</td>
      <td>Cor ou raça</td>
      <td>Campo Obrigatório</td>
      <td>CS_RACA</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 4&lt;/page_number&gt;</footer>

---


## Page 5

<table>
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td></td>
      <td></td>
      <td>2-Preta<br>3-Amarela<br>4-Parda<br>5-Indígena<br>9-Ignorado</td>
      <td>declarada pelo paciente:<br>Branca; Preta;<br>Amarela; Parda (pessoa que se declarou mulata,<br>cabocla, cafuza,<br>mameluca ou<br>mestiça de preto com pessoa de outra cor ou raça);<br>e, Indígena.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>16-Se indígena, qual etnia?</td>
      <td>Varchar2(4)</td>
      <td>Tabela do SIASI com código e nomes das etnias indígenas.</td>
      <td>Nome e código da etnia do paciente, quando indígena.</td>
      <td>Campo Essencial<br>Habilitado se campo 15-Raça/Cor for igual a 5-Indígena.</td>
      <td>CS_ETINIA</td>
    </tr>
    <tr>
      <td>17- É membro de povo ou comunidade tradicional?</td>
      <td>Varchar 2(1)</td>
      <td>1-Sim<br>2-Não</td>
      <td>Informar se o paciente for membro de algum povo ou comunidade tradicional</td>
      <td>Campo Obrigatório</td>
      <td>POV_CT</td>
    </tr>
    <tr>
      <td>18- Se sim, qual?</td>
      <td>Varchar 2(100)</td>
      <td>Tabela de Povos e Comunidades Tradicionais</td>
      <td>Informar o povo ou comunidade tradicional</td>
      <td>Campo Obrigatório- Habilitado se campo 17- É membro de povo ou comunidade tradicional? for igual a 1- Sim</td>
      <td>TP_POV_CT</td>
    </tr>
    <tr>
      <td>19-Escolaridade</td>
      <td>Varchar2(1)</td>
      <td>0-Sem escolaridade/<br>Analfabeto<br>1-Fundamental 1º ciclo (1ª a 5ª série)<br>2-Fundamental 2º ciclo (6ª a 9ª série)<br>3- Médio (1º ao 3º ano)<br>4-Superior<br>5-Não se aplica<br>9-Ignorado</td>
      <td>Nível de escolaridade do paciente.<br>Para os níveis fundamental e médio deve ser considerada a última série ou ano concluído.</td>
      <td>Campo Essencial<br>Preenchido automaticamente com a categoria “não se aplica” quando idade for menor que 7 anos<br>Quando idade for maior que 7 anos, o campo não pode ser preenchido com “não se aplica”.</td>
      <td>CS_ESCOL_N</td>
    </tr>
    <tr>
      <td>20- Ocupação</td>
      <td>Varchar2(6)</td>
      <td>Tabela com código da Ocupação da Classificação Brasileira de Ocupações (CBO).</td>
      <td>Ocupação profissional do paciente</td>
      <td>Campo Essencial</td>
      <td>PAC_COCBO ou PAC_DSCBO</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 5&lt;/page_number&gt;</footer>

---


## Page 6

<table>
  <tr>
    <td>21-Nome da mãe</td>
    <td>Varchar2(70)</td>
    <td></td>
    <td>Nome completo da mãe do paciente (sem abreviações).</td>
    <td>Campo Essencial</td>
    <td>NM_MAE_PAC</td>
  </tr>
  <tr>
    <td>22-CEP</td>
    <td>Varchar2(8)</td>
    <td></td>
    <td>CEP de residência do paciente.</td>
    <td>Campo Essencial<br>Validado a partir da tabela de CEP dos Correios.</td>
    <td>NU_CEP</td>
  </tr>
  <tr>
    <td>23-UF</td>
    <td>Varchar2(2)</td>
    <td>Tabela com código e siglas das UF padronizados pelo IBGE.</td>
    <td>Unidade Federativa de residência do paciente.</td>
    <td>Campo Obrigatório<br>Se campo 31-País for Brasil.<br><br>Se preenchido o campo CEP, a UF é preenchida automaticamente pelo sistema e desabilitada para edição.</td>
    <td>SG_UF</td>
  </tr>
  <tr>
    <td>Regional de Saúde de Residência Código (IBGE)</td>
    <td>Varchar2 (6)</td>
    <td>Tabela com código e nomes das Regionais de Saúde dos municípios de residência padronizados pelo IBGE.</td>
    <td>Regional de Saúde onde está localizado o Município de residência do paciente.</td>
    <td>Campo Interno<br>Preenchendo o nome da regional de saúde de residência, o código é preenchido automaticamente, e vice-versa;</td>
    <td>ID_RG_RESI OU CO_RG_RESI</td>
  </tr>
  <tr>
    <td>24-Município Código (IBGE)</td>
    <td>Varchar2(6)</td>
    <td>Tabela com código e nome dos Municípios padronizados pelo IBGE.</td>
    <td>Município de residência do paciente.</td>
    <td>Campo Obrigatório<br>Se campo 31-País for Brasil.<br><br>Se preenchido o campo CEP, o Município e seu respectivo código IBGE são preenchidos automaticamente pelo sistema e desabilitados para edição.<br><br>Se o CEP não for preenchido, o campo é habilitado depois de selecionada uma UF no campo 23. Nesse caso, o sistema abre tabela com os municípios da UF.<br><br>Preenchendo o nome do município, o código é preenchido automaticamente, ou vice-versa.</td>
    <td>ID_MN_RESI OU CO_MUN_RES</td>
  </tr>
  <tr>
    <td>25-Bairro</td>
    <td>Varchar2(72)</td>
    <td>Tabela com código e nome dos Bairros padronizados pelos Correios.</td>
    <td>Bairro de residência do paciente.</td>
    <td>Campo Essencial<br>Se preenchido o campo CEP, o Bairro é preenchido automaticamente pelo sistema.</td>
    <td>NM_BAIRRO</td>
  </tr>
  <tr>
    <td>26-Logradouro (Rua, Avenida, etc.)</td>
    <td>Varchar2(50)</td>
    <td>Tabela com código e nome dos logradouros padronizados pelos Correios.</td>
    <td>Logradouro (rua, avenida, quadra, travessa, etc.) do endereço de residência do</td>
    <td>Campo Essencial<br>Se preenchido o campo CEP, o logradouro é preenchido automaticamente pelo sistema.</td>
    <td>NM_LOGRADO</td>
  </tr>
</table>

SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 6&lt;/page_number&gt;

---


## Page 7

<table>
  <thead>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>27-Nº</td>
      <td>Varchar2(8)</td>
      <td></td>
      <td>Nº do logradouro (nº da casa ou do edifício).</td>
      <td>Campo Essencial</td>
      <td>NU_NUMERO</td>
    </tr>
    <tr>
      <td>28-Complemento (apto, casa, etc.)</td>
      <td>Varchar2(15)</td>
      <td></td>
      <td>Complemento do logradouro (bloco, apto, casa, etc.).</td>
      <td>Campo Essencial</td>
      <td>NM_COMPLEM</td>
    </tr>
    <tr>
      <td>29-(DDD) Telefone</td>
      <td>Varchar2(4)<br>Varchar2(10)</td>
      <td></td>
      <td>Código DDD e número de telefone para contato do paciente.</td>
      <td>Campo Essencial</td>
      <td>NU_DDD_TEL OU NU_TELEFON</td>
    </tr>
    <tr>
      <td>30-Zona</td>
      <td>Varchar2(1)</td>
      <td>1-Urbana<br>2-Rural<br>3-Periurbana<br>9-Ignorado</td>
      <td>Zona geográfica do endereço de residência do paciente.</td>
      <td>Campo Essencial</td>
      <td>CS_ZONA</td>
    </tr>
    <tr>
      <td>31-País (se residente fora do Brasil)</td>
      <td>Varchar2(3)</td>
      <td>Tabela com código e nome dos Países.</td>
      <td>País de residência do paciente.</td>
      <td>Campo Obrigatório<br><br>Se preenchido CEP, ou for selecionada uma UF, o campo País é preenchido automaticamente pelo sistema e desabilitado para edição.<br><br>Se selecionado País diferente de Brasil, os campos 22 a 28 são desabilitados.</td>
      <td>ID_PAIS OU CO_PAIS</td>
    </tr>
    <tr>
      <td>32-Trata-se de caso nosocomial (infecção adquirida no hospital)?</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Caso de SRAG com infecção adquirida após internação.</td>
      <td>Campo Essencial<br><br>Quando o campo 32 for igual a 1, é permitido digitar data de início dos sintomas posterior a data de internação.</td>
      <td>NOSOCOMIAL</td>
    </tr>
    <tr>
      <td>33- Paciente trabalha ou tem contato direto com aves, suínos, ou outro animal?</td>
      <td>Varchar2(1)</td>
      <td>1-Sim, aves e/ou suínos<br>2-Não, nenhum<br>3- Sim, outros, qual<br>9-ignorado</td>
      <td>Paciente teve contato direto ou trabalha com aves, suínos ou outro animal?</td>
      <td>Campo Essencial</td>
      <td>AVE_SUINO</td>
    </tr>
    <tr>
      <td>33-Paciente trabalha ou tem contato direto com aves, suínos/Outro animal (especificar)</td>
      <td>Varchar2(60)</td>
      <td></td>
      <td>Paciente teve contato direto ou trabalha com outro animal.</td>
      <td>Campo Essencial<br><br>Habilitado de campo 33- Contato com outro animal = 3 (Outro).</td>
      <td>OUT_ANIM</td>
    </tr>
    <tr>
      <td>34-Sinais e Sintomas/Febre</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente apresentou febre?</td>
      <td>Campo Essencial</td>
      <td>FEBRE</td>
    </tr>
    <tr>
      <td>34-Sinais e Sintomas/Tosse</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim</td>
      <td>Paciente</td>
      <td>Campo Essencial</td>
      <td>TOSSE</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 7&lt;/page_number&gt;</footer>

---


## Page 8

<table>
  <thead>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>34-Sinais e Sintomas/Dor de Garganta</td>
      <td>Varchar2(1)</td>
      <td>2-Não<br>9-Ignorado</td>
      <td>apresentou tosse?</td>
      <td></td>
      <td>GARGANTA</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente apresentou dor de garganta?</td>
      <td>Campo Essencial</td>
      <td></td>
    </tr>
    <tr>
      <td>34-Sinais e Sintomas/Dispneia</td>
      <td>Varchar2(1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente apresentou dispneia?</td>
      <td>Campo Essencial</td>
      <td>DISPNEIA</td>
    </tr>
    <tr>
      <td>34-Sinais e Sintomas/Desconforto Respiratório</td>
      <td>Varchar2(1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente apresentou desconforto respiratório?</td>
      <td>Campo Essencial</td>
      <td>DESC_RESP</td>
    </tr>
    <tr>
      <td>34-Sinais e Sintomas/Saturação O₂&lt; 95%</td>
      <td>Varchar2(1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente apresentou saturação O₂&lt; 95%?</td>
      <td>Campo Essencial</td>
      <td>SATURACAO</td>
    </tr>
    <tr>
      <td>34-Sinais e Sintomas/Diarreia</td>
      <td>Varchar2(1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente apresentou diarreia?</td>
      <td>Campo Essencial</td>
      <td>DIARREIA</td>
    </tr>
    <tr>
      <td>34-Sinais e Sintomas/Vômito</td>
      <td>Varchar2(1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente apresentou vômito?</td>
      <td>Campo Essencial</td>
      <td>VOMITO</td>
    </tr>
    <tr>
      <td>34-Sinais e Sintomas/Dor abdominal</td>
      <td>Varchar2(1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente apresentou dor abdominal?</td>
      <td>Campo Essencial</td>
      <td>DOR_ABD</td>
    </tr>
    <tr>
      <td>34-Sinais e Sintomas/Fadiga</td>
      <td>Varchar2(1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente apresentou fadiga?</td>
      <td>Campo Essencial</td>
      <td>FADIGA</td>
    </tr>
    <tr>
      <td>34-Sinais e Sintomas/Perda do Olfato</td>
      <td>Varchar2(1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente apresentou perda do olfato?</td>
      <td>Campo Essencial</td>
      <td>PERD_OLFT</td>
    </tr>
    <tr>
      <td>34-Sinais e Sintomas/Perda do Paladar</td>
      <td>Varchar2(1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente apresentou perda do paladar?</td>
      <td>Campo Essencial</td>
      <td>PERD_PALA</td>
    </tr>
    <tr>
      <td>34-Sinais e Sintomas/Outros</td>
      <td>Varchar2(1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente apresentou outro(s) sintoma(s)?</td>
      <td>Campo Essencial</td>
      <td>OUTRO_SIN</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 8&lt;/page_number&gt;</footer>

---


## Page 9

<table>
  <thead>
    <tr>
      <td>34-Sinais e Sintomas/Outros (Descrição)</td>
      <td>Varchar2(30)</td>
      <td></td>
      <td>Listar outros sinais e sintomas apresentados pelo paciente.</td>
      <td>Campo Essencial<br>Habilitado se selecionado categoria 1-Sim em Sinais e Sintomas/Outros.</td>
      <td>OUTRO_DES</td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>35-Fatores de risco</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente apresenta algum fator de risco</td>
      <td>Campo Essencial</td>
      <td>FATOR_RISC</td>
    </tr>
    <tr>
      <td>35-Fatores de risco/ Puérpera</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente é puérpera ou parturiente (mulher que pariu recentemente – até 45 dias do parto)?</td>
      <td>Campo Essencial<br>Habilitado se selecionado no campo 8- Sexo Feminino.</td>
      <td>PUERPERA</td>
    </tr>
    <tr>
      <td>35-Fatores de risco/ Doença Cardiovascular Crônica</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente possui Doença Cardiovascular Crônica?</td>
      <td>Campo Essencial</td>
      <td>CARDIOPATI</td>
    </tr>
    <tr>
      <td>35-Fatores de risco/ Doença Hematológica Crônica</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente possui Doença Hematológica Crônica?</td>
      <td>Campo Essencial</td>
      <td>HEMATOLOGI</td>
    </tr>
    <tr>
      <td>35-Fatores de risco/ Síndrome de Down</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente possui Síndrome de Down?</td>
      <td>Campo Essencial</td>
      <td>SIND_DOWN</td>
    </tr>
    <tr>
      <td>35-Fatores de risco/ Doença Hepática Crônica</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente possui Doença Hepática Crônica?</td>
      <td>Campo Essencial</td>
      <td>HEPATICA</td>
    </tr>
    <tr>
      <td>35-Fatores de risco/ Asma</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente possui Asma?</td>
      <td>Campo Essencial</td>
      <td>ASMA</td>
    </tr>
    <tr>
      <td>35-Fatores de risco/ Diabetes mellitus</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente possui Diabetes mellitus?</td>
      <td>Campo Essencial</td>
      <td>DIABETES</td>
    </tr>
    <tr>
      <td>35-Fatores de risco/ Doença Neurológica Crônica</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente possui Doença Neurológica?</td>
      <td>Campo Essencial</td>
      <td>NEUROLOGIC</td>
    </tr>
    <tr>
      <td>35-Fatores de risco/ Outra Pneumopatia Crônica</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não</td>
      <td>Paciente possui outra pneumopatia</td>
      <td>Campo Essencial</td>
      <td>PNEUMOPATI</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 9&lt;/page_number&gt;</footer>

---


## Page 10

<table>
  <thead>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td></td>
      <td></td>
      <td>9-Ignorado</td>
      <td>crônica?</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>35-Fatores de risco/ Imunodeficiência ou Imunodepressão</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente possui Imunodeficiência ou Imunodepressão (diminuição da função do sistema imunológico)?</td>
      <td>Campo Essencial</td>
      <td>IMUNODEPRE</td>
    </tr>
    <tr>
      <td>35-Fatores de risco/ Doença Renal Crônica</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente possui Doença Renal Crônica?</td>
      <td>Campo Essencial</td>
      <td>RENAL</td>
    </tr>
    <tr>
      <td>35-Fatores de risco/ Obesidade</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente possui obesidade?</td>
      <td>Campo Essencial</td>
      <td>OBESIDADE</td>
    </tr>
    <tr>
      <td>35-Fatores de risco/ Obesidade (Descrição IMC)</td>
      <td>Varchar2(3)</td>
      <td></td>
      <td>Valor do IMC (Índice de Massa Corporal) do paciente calculado pelo profissional de saúde.</td>
      <td>Campo Essencial<br>Habilitado se selecionado categoria 1-Sim em Fatores de risco/Obesidade.</td>
      <td>OBES_IMC</td>
    </tr>
    <tr>
      <td>35-Fatores de risco/ Tabagismo</td>
      <td>Varchar2(1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente é tabagista?</td>
      <td>Campo Essencial</td>
      <td>TABAG</td>
    </tr>
    <tr>
      <td>35-Fatores de risco/ Outros</td>
      <td>Varchar2(1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Paciente possui outro(s) fator(es) de risco?</td>
      <td>Campo Essencial</td>
      <td>OUT_MORBI</td>
    </tr>
    <tr>
      <td>35-Fatores de risco/ Outros (Descrição)</td>
      <td>Varchar2(30)</td>
      <td></td>
      <td>Listar outro(s) fator(es) de risco do paciente.</td>
      <td>Campo Essencial<br>Habilitado se selecionado categoria 1-Sim em Fatores de risco/Outros.</td>
      <td>MORB_DESC</td>
    </tr>
    <tr>
      <td>36- Recebeu vacina COVID-19?</td>
      <td>Varchar(1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Informar se o paciente recebeu vacina COVID-19, após verificar a documentação / caderneta.</td>
      <td>Campo Obrigatório<br>*Integração com a Base Nacional de Vacinação</td>
      <td>VACINA_COV</td>
    </tr>
    <tr>
      <td>37- Data 1ª dose da vacina COVID-19</td>
      <td>Varchar(10)</td>
      <td>Date<br>DD/MM/AAAA</td>
      <td>Informar a data em que o paciente recebeu a 1ª dose da vacina COVID-19</td>
      <td>Campo essencial<br>*Integração com a Base Nacional de Vacinação</td>
      <td>DOSE_1_COV</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 10&lt;/page_number&gt;</footer>

---


## Page 11

<table>
  <tr>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td>Habilitado se campo 36- Recebeu vacina COVID-19? for igual a 1.</td>
    <td></td>
  </tr>
  <tr>
    <td>37- Data 2ª dose da vacina COVID-19</td>
    <td>Varchar(10)</td>
    <td>Date<br>DD/MM/AAAA</td>
    <td>Informar a data em que o paciente recebeu a 2ª dose da vacina COVID-19</td>
    <td>Campo essencial<br>*Integração com a Base Nacional de Vacinação<br><br>Habilitado se campo 36- Recebeu vacina COVID-19? for igual a 1.</td>
    <td>DOSE_2_COV</td>
  </tr>
  <tr>
    <td>37- Data da dose reforço da vacina COVID-19</td>
    <td>Varchar(10)</td>
    <td>Date<br>DD/MM/AAAA</td>
    <td>Informar a data em que o paciente recebeu a dose reforço</td>
    <td>Campo essencial<br>*Integração com a Base Nacional de Vacinação<br><br>Habilitado se campo 36- Recebeu vacina COVID-19? for igual a 1.</td>
    <td>DOSE_REF</td>
  </tr>
  <tr>
    <td>37- Data da 2ª dose reforço da vacina COVID-19</td>
    <td>Varchar(10)</td>
    <td>Date<br>DD/MM/AAAA</td>
    <td>Informar a data em que o paciente recebeu a 2ª dose reforço</td>
    <td>Campo essencial<br>*Integração com a Base Nacional de Vacinação<br><br>Habilitado se campo 36- Recebeu vacina COVID-19? for igual a 1.</td>
    <td>DOSE_2REF</td>
  </tr>
  <tr>
    <td>37- Data da dose adicional da vacina COVID-19</td>
    <td>Varchar(10)</td>
    <td>Date<br>DD/MM/AAAA</td>
    <td>Informar a data em que o paciente recebeu a dose adicional da vacina COVID-19</td>
    <td>Campo essencial<br>*Integração com a Base Nacional de Vacinação<br><br>Habilitado se campo 36- Recebeu vacina COVID-19? for igual a 1.</td>
    <td>DOSE_ADIC</td>
  </tr>
  <tr>
    <td>37- Data dose reforço bivalente COVID-19</td>
    <td>Varchar(10)</td>
    <td>Date<br>DD/MM/AAAA</td>
    <td>Informar a data em que o paciente recebeu a dose reforço bivalente COVID-19</td>
    <td>Campo essencial<br>*Integração com a Base Nacional de Vacinação<br><br>Habilitado se campo 36- Recebeu vacina COVID-19? for igual a 1.</td>
    <td>DOS_RE_BI</td>
  </tr>
  <tr>
    <td>38- Fabricante 1ª dose da vacina COVID-19</td>
    <td>Varchar(80)</td>
    <td></td>
    <td>Informar o fabricante da vacina, que o paciente recebeu na primeira dose</td>
    <td>Campo essencial<br>*Integração com a Base Nacional de Vacinação<br><br>Habilitado se campo 36- Recebeu vacina COVID-19? for igual a 1.</td>
    <td>FAB_COV1</td>
  </tr>
  <tr>
    <td>38- Fabricante 2ª dose da vacina COVID-19</td>
    <td>Varchar(80)</td>
    <td></td>
    <td>Informar o fabricante da vacina, que o paciente recebeu na segunda dose</td>
    <td>Campo essencial<br>*Integração com a Base Nacional de Vacinação<br><br>Habilitado se campo 36- Recebeu vacina COVID-19? for igual a 1.</td>
    <td>FAB_COV2</td>
  </tr>
  <tr>
    <td>38- Fabricante dose reforço da vacina COVID-19</td>
    <td>Varchar(80)</td>
    <td></td>
    <td>Informar o fabricante da vacina, que o</td>
    <td>Campo essencial<br>*Integração com a Base Nacional de Vacinação</td>
    <td>FAB_COVRF</td>
  </tr>
</table>

SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 11&lt;/page_number&gt;

---


## Page 12

<table>
  <thead>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>38- Fabricante 2ª dose reforço da vacina COVID-19</td>
      <td>Varchar(80)</td>
      <td></td>
      <td>paciente recebeu na dose reforço</td>
      <td>Habilitado se campo 36- Recebeu vacina COVID-19? for igual a 1.</td>
      <td>FAB_COVRF2</td>
    </tr>
    <tr>
      <td>38- Fabricante dose adicional da vacina COVID-19</td>
      <td>Varchar(80)</td>
      <td></td>
      <td>Informar o fabricante da vacina, que o paciente recebeu na dose adicional</td>
      <td>Campo essencial<br>*Integração com a Base Nacional de Vacinação<br><br>Habilitado se campo 36- Recebeu vacina COVID-19? for igual a 1.</td>
      <td>FAB_ADIC</td>
    </tr>
    <tr>
      <td>38- Fabricante dose reforço bivalente COVID-19</td>
      <td>Varchar(80)</td>
      <td></td>
      <td>Informar o fabricante da vacina, que o paciente recebeu na dose reforço bivalente</td>
      <td>Campo essencial<br>*Integração com a Base Nacional de Vacinação<br><br>Habilitado se campo 36- Recebeu vacina COVID-19? for igual a 1.</td>
      <td>FAB_RE_BI</td>
    </tr>
    <tr>
      <td>39- Lote da vacina COVID-19: Lote 1ª Dose</td>
      <td>Varchar(20)</td>
      <td></td>
      <td>Informar o Lote da 1ª dose da vacina COVID-19, que o paciente recebeu</td>
      <td>Campo essencial<br>*Integração com a Base Nacional de Vacinação<br><br>Habilitado se campo 36- Recebeu vacina COVID-19? for igual a 1.</td>
      <td>LOTE_1_COV</td>
    </tr>
    <tr>
      <td>39- Lote da vacina COVID-19: Lote 2ª Dose</td>
      <td>Varchar(20)</td>
      <td></td>
      <td>Informar o Lote da 2ª dose da vacina COVID-19, que o paciente recebeu</td>
      <td>Campo essencial<br>*Integração com a Base Nacional de Vacinação<br><br>Habilitado se campo 36- Recebeu vacina COVID-19? for igual a 1.</td>
      <td>LOTE_2_COV</td>
    </tr>
    <tr>
      <td>39- Lote da vacina COVID-19: Lote dose reforço</td>
      <td>Varchar(20)</td>
      <td></td>
      <td>Informar o Lote da dose reforço da vacina COVID-19, que o paciente recebeu</td>
      <td>Campo essencial<br>*Integração com a Base Nacional de Vacinação<br><br>Habilitado se campo 36- Recebeu vacina COVID-19? for igual a 1.</td>
      <td>LOTE_REF</td>
    </tr>
    <tr>
      <td>39- Lote da vacina COVID-19: Lote 2ª dose reforço</td>
      <td>Varchar(20)</td>
      <td></td>
      <td>Informar o Lote da 2ª dose reforço da vacina COVID-19, que o paciente recebeu</td>
      <td>Campo essencial<br>*Integração com a Base Nacional de Vacinação<br><br>Habilitado se campo 36- Recebeu vacina COVID-19? for igual a 1.</td>
      <td>LOTE_REF2</td>
    </tr>
    <tr>
      <td>39- Lote da vacina COVID-19 Dose</td>
      <td>Varchar(20)</td>
      <td></td>
      <td>Informar o Lote da</td>
      <td>Campo essencial</td>
      <td>LOTE_ADIC</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 12&lt;/page_number&gt;</footer>

---


## Page 13

<table>
  <thead>
    <tr>
      <td>adicional</td>
      <td></td>
      <td></td>
      <td>dose adicional da vacina COVID-19, que o paciente recebeu</td>
      <td>*Integração com a Base Nacional de Vacinação<br>Habilitado se campo 36- Recebeu vacina COVID-19? for igual a 1.</td>
      <td></td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>39- Lote da vacina COVID-19 reforço bivalente</td>
      <td>Dose</td>
      <td>Varchar(20)</td>
      <td>Informar o Lote da dose reforço bivalente da vacina COVID-19, que o paciente recebeu</td>
      <td>Campo essencial<br>*Integração com a Base Nacional de Vacinação<br>Habilitado se campo 36- Recebeu vacina COVID-19? for igual a 1.</td>
      <td>LOT_RE_BI</td>
    </tr>
    <tr>
      <td>39- Fonte dos dados/informação sobre a vacina COVID-19</td>
      <td></td>
      <td>Varchar(1)</td>
      <td>1- Manual<br>2- Integração</td>
      <td>Campo Interno<br>Número gerado automaticamente pelo sistema.<br><br>Campo preenchido de acordo com a fonte dos dados/informação sobre a vacina COVID-19, se foi digitada manualmente ou recuperada via integração com a Base Nacional de Vacinação.</td>
      <td>FNT_IN_COV</td>
    </tr>
    <tr>
      <td>40-Recebeu vacina contra Gripe na última campanha?</td>
      <td></td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Informar se o paciente foi vacinado contra gripe na última campanha, após verificar a documentação / caderneta.<br><br>Caso o paciente não tenha a caderneta, direcionar a pergunta para ele ou responsável e preencher o campo com o código correspondente a resposta.</td>
      <td>VACINA</td>
    </tr>
    <tr>
      <td>41-Data da vacinação</td>
      <td></td>
      <td>Date<br>DD/MM/AAAA</td>
      <td>Data da última dose de vacina contra gripe que o paciente tomou.</td>
      <td>Campo Essencial<br><br>Habilitado se campo 40-Recebeu vacina contra Gripe na última campanha? for igual a 1.<br><br>Data deve ser <= a data da digitação (data atual).</td>
      <td>DT_UT_DOSE</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 13&lt;/page_number&gt;</footer>

---


## Page 14

<table>
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Se &lt; 6 meses: a mãe recebeu a vacina?</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Se paciente &lt; 6 meses, a mãe recebeu vacina?</td>
      <td>Campo Essencial<br>Habilitar campo<br>Se a Idade do caso for &lt; 6 meses.</td>
      <td>MAE_VAC</td>
    </tr>
    <tr>
      <td>Se sim, data</td>
      <td>Date<br>DD/MM/AAAA</td>
      <td></td>
      <td>Se a mãe recebeu vacina, qual a data?</td>
      <td>Campo Essencial<br>Habilitado se campo<br>Se &lt; 6 meses: a mãe recebeu a vacina for igual a 1.<br>Data deve ser <= a data da digitação (data atual).</td>
      <td>DT_VAC_MAE</td>
    </tr>
    <tr>
      <td>Se &lt; 6 meses: a mãe amamenta a criança?</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Se paciente &lt; 6 meses, a mãe amamenta a criança?</td>
      <td>Campo Essencial<br>Habilitar campo se<br>Se a Idade do caso for &lt; 6 meses.</td>
      <td>M_AMAMENTA</td>
    </tr>
    <tr>
      <td>Se &gt;= 6 meses e &lt;= 8 anos: Data da dose única 1/1</td>
      <td>Date<br>DD/MM/AAAA</td>
      <td></td>
      <td>Se &gt;= 6 meses e &lt;= 8 anos, data da dose única para crianças vacinadas em campanhas de anos anteriores</td>
      <td>Campo Essencial<br>Habilitar campo<br>Se a Idade do caso for &gt;= 6 meses e &lt;= 8 anos</td>
      <td>DT_DOSEUNI</td>
    </tr>
    <tr>
      <td>Se &gt;= 6 meses e &lt;= 8 anos: Data da 1ª dose</td>
      <td>Date<br>DD/MM/AAAA</td>
      <td></td>
      <td>Se &gt;= 6 meses e &lt;= 8 anos, data da 1ª dose para crianças vacinadas pela primeira vez</td>
      <td>Campo Essencial<br>Habilitar campo<br>Se a Idade do caso for &gt;= 6 meses e &lt;= 8 anos</td>
      <td>DT_1_DOSE</td>
    </tr>
    <tr>
      <td>Se &gt;= 6 meses e &lt;= 8 anos: Data da 2ª dose</td>
      <td>Date<br>DD/MM/AAAA</td>
      <td></td>
      <td>Se &gt;= 6 meses e &lt;= 8 anos data da 2ª dose para crianças vacinadas pela primeira vez</td>
      <td>Campo Essencial<br>Habilitar campo<br>Se a Idade do caso for &gt;= 6 meses e &lt;= 8 anos</td>
      <td>DT_2_DOSE</td>
    </tr>
    <tr>
      <td>42-Usou antiviral para gripe?</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Fez uso de antiviral para tratamento da doença?</td>
      <td>Campo Essencial</td>
      <td>ANTIVIRAL</td>
    </tr>
    <tr>
      <td>43-Qual antiviral?</td>
      <td>Varchar2 (1)</td>
      <td>1- Oseltamivir<br>2- Zanamivir<br>3- Outro, especifique</td>
      <td>Qual antiviral utilizado?</td>
      <td>Campo Essencial<br>Habilitado se campo 42-Usou antiviral para gripe? for igual a 1.</td>
      <td>TP_ANTIVIR</td>
    </tr>
    <tr>
      <td>Qual antiviral /Outro, especifique</td>
      <td>Varchar2(30)</td>
      <td></td>
      <td>Se o antiviral</td>
      <td>Campo Essencial</td>
      <td>OUT_ANTIV</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 14&lt;/page_number&gt;</footer>

---


## Page 15

<table>
  <tr>
    <td></td>
    <td></td>
    <td></td>
    <td>utilizado não foi Oseltamivir ou Zanamivir, informar qual antiviral foi utilizado.</td>
    <td>Habilitado se campo 40- Qual antiviral? for igual a 3.</td>
    <td></td>
  </tr>
  <tr>
    <td>44-Data do início do tratamento</td>
    <td>Date<br>DD/MM/AAAA</td>
    <td></td>
    <td>Data em que foi iniciado o tratamento com o antiviral.</td>
    <td>Campo Essencial<br>Habilitado se campo 42-Usou antiviral para gripe? for igual a 1.<br>Data deve ser <= a data da digitação (data atual).</td>
    <td>DT_ANTIVIR</td>
  </tr>
  <tr>
    <td>45-Recebeu tratamento antiviral para covid-19?</td>
    <td>Varchar2(1)</td>
    <td>1-Sim<br>2-Não<br>9-Ignorado</td>
    <td>Fez uso de antiviral para tratamento de covid-19?</td>
    <td>Campo Essencial</td>
    <td>TRAT_COV</td>
  </tr>
  <tr>
    <td>46- Qual antiviral?</td>
    <td>Varchar2(1)</td>
    <td>1-Nirmatrevir/ritonavir (Paxlovid ®)<br>2- Molnupiravir(Lagevrio®)<br>3- Baricitinibe (Olumiant®)<br>4- Outro, especifique</td>
    <td>Se foi feito uso de antiviral para tratamento de covid-19, informar qual, conforme relação disponível.</td>
    <td>Habilitado se campo 45-Recebeu tratamento antiviral para covid-19? for igual a 1.</td>
    <td>TIPO_TRAT</td>
  </tr>
  <tr>
    <td>Qual antiviral /Outro, especifique</td>
    <td>Varchar2(30)</td>
    <td></td>
    <td>Se o antiviral utilizado não foi, 1- Nirmatrevir/ritonavir (Paxlovid ®) 2- Molnupiravir (Lagevrio®) 3- Baricitinibe (Olumiant®), informar qual antiviral foi utilizado.</td>
    <td>Campo Essencial<br>Habilitado se campo 46- Qual antiviral? for igual a 4.</td>
    <td>OUT_TRAT</td>
  </tr>
  <tr>
    <td>47- Data do início do tratamento</td>
    <td>Date<br>DD/MM/AAAA</td>
    <td></td>
    <td>Data em que foi iniciado o tratamento com o antiviral, para tratamento de covid-19.</td>
    <td>Campo Essencial<br>Habilitado se campo 45-Recebeu tratamento antiviral para covid-19? for igual a 1.<br>Data deve ser <= a data da digitação (data atual).</td>
    <td>DT_TRT_COV</td>
  </tr>
  <tr>
    <td>48-Houve internação?</td>
    <td>Varchar2(1)</td>
    <td>1-Sim<br>2-Não<br>9-Ignorado</td>
    <td>O paciente foi internado?</td>
    <td>Campo Essencial<br>Caso o campo não seja igual a 1 - Sim o sistema emitirá um aviso indicando que não atende a definição de caso.</td>
    <td>HOSPITAL</td>
  </tr>
</table>

SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 15&lt;/page_number&gt;

---


## Page 16

<table>
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>49-Data da internação por SRAG</td>
      <td>Date<br>DD/MM/AAAA</td>
      <td>Data em que o paciente foi hospitalizado.</td>
      <td>Campo Obrigatório<br>Data deve ser maior ou igual a 2- Data de 1ºs sintomas e menor ou igual a data da digitação (atual).</td>
      <td>DT_INTERNA</td>
    </tr>
    <tr>
      <td>50-UF de internação</td>
      <td>Varchar2(2)</td>
      <td>Unidade Federativa de internação do paciente.</td>
      <td>Campo Essencial<br>Habilitado se campo 48-Houve internação? for igual a 1</td>
      <td>SG_UF_INTE</td>
    </tr>
    <tr>
      <td>Regional de Saúde de Internação Código (IBGE)</td>
      <td>Varchar2 (6)</td>
      <td>Regional de Saúde onde está localizado o Município de internação do paciente.</td>
      <td>Campo Interno<br>Preenchendo o nome da regional de saúde de internação, o código é preenchido automaticamente, e vice-versa.</td>
      <td>ID_RG_INTE OU CO_RG_INTE</td>
    </tr>
    <tr>
      <td>51-Município de internação/Código(IBGE)</td>
      <td>Varchar2 (20)</td>
      <td>Município onde está localizado a Unidade de Saúde onde o paciente internou.</td>
      <td>Campo Essencial<br>Habilitado se campo 48-Houve internação? for igual a 1</td>
      <td>ID_MN_INTE OU CO_MU_INTE</td>
    </tr>
    <tr>
      <td>52-Unidade de Saúde de internação/Código CNES</td>
      <td>Varchar2(20)</td>
      <td>Unidade que realizou a internação do paciente.</td>
      <td>Campo Essencial<br>Habilitado se campo 48-Houve internação? for igual a 1</td>
      <td>ID_UN_INTE OU CO_UN_INTE</td>
    </tr>
    <tr>
      <td>53-Internado em UTI?</td>
      <td>Varchar2(1)</td>
      <td>O paciente foi internado em UTI?</td>
      <td>Campo Essencial</td>
      <td>UTI</td>
    </tr>
    <tr>
      <td>54-Data da entrada na UTI</td>
      <td>Date<br>DD/MM/AAAA</td>
      <td>Data de entrada do paciente na unidade de Terapia intensiva (UTI).</td>
      <td>Campo Essencial<br>Habilitado se campo 53-Internado em UTI? for igual a 1.<br>Data deve ser maior ou igual a 2-Data de 1ºs sintomas da SRAG e menor ou igual a data da digitação (atual).</td>
      <td>DT_ENTUTI</td>
    </tr>
    <tr>
      <td>55-Data da saída da UTI</td>
      <td>Date<br>DD/MM/AAAA</td>
      <td>Data em que o paciente saiu da Unidade de Terapia intensiva (UTI).</td>
      <td>Campo Essencial<br>Habilitado se campo 53-Internado em UTI? for igual a 1.<br>Data deve ser maior ou igual a 54-Data da entrada na UTI e menor ou igual a data da digitação (atual).</td>
      <td>DT_SAIDUTI</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 16&lt;/page_number&gt;</footer>

---


## Page 17

<table>
  <thead>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>56-Uso de suporte ventilatório?</td>
      <td>Varchar2(1)</td>
      <td>1-Sim, invasivo<br>2-Sim, não invasivo<br>3-Não<br>9-Ignorado</td>
      <td>O paciente fez uso de suporte ventilatório?</td>
      <td>Campo Essencial</td>
      <td>SUPPORT_VEN</td>
    </tr>
    <tr>
      <td>57- Raio X de Tórax</td>
      <td>Varchar2(1)</td>
      <td>1-Normal<br>2-Infiltrado intersticial<br>3-Consolidação<br>4-Misto<br>5-Outro<br>6-Não realizado<br>9-Ignorado</td>
      <td>Informar resultado de Raio X de Tórax.</td>
      <td>Campo Essencial</td>
      <td>RAIOX_RES</td>
    </tr>
    <tr>
      <td>Raio X de Tórax/ Outro (especificar)</td>
      <td>Varchar2(30)</td>
      <td></td>
      <td>Informar o resultado do RX de tórax se selecionado a opção 5-Outro.</td>
      <td>Campo Essencial<br>Habilitado de campo 57- Raio X de Tórax = 5 (Outro).</td>
      <td>RAIOX_OUT</td>
    </tr>
    <tr>
      <td>58-Data do Raio X</td>
      <td>Data<br>DD/MM/AAAA</td>
      <td></td>
      <td>Se realizou RX de Tórax, especificar a data do exame.</td>
      <td>Campo Essencial<br>Habilitado se campo 57- Raio X de Tórax for igual a 1, 2, 3, 4 ou 5.</td>
      <td>DT_RAIOX</td>
    </tr>
    <tr>
      <td>59- Aspecto Tomografia</td>
      <td>Number(3)</td>
      <td>1-Tipico covid-19<br>2- Indeterminado covid-19<br>3- Atípico covid-19<br>4- Negativo para Pneumonia<br>5- Outro<br>6-Não realizado<br>9-Ignorado</td>
      <td>Informar o resultado da tomografia.</td>
      <td>Campo Essencial</td>
      <td>TOMO_RES</td>
    </tr>
    <tr>
      <td>Aspecto Tomografia/Outro (especificar)</td>
      <td>Varchar2(100)</td>
      <td></td>
      <td>Informar o resultado da tomografia se selecionado a opção 5-Outro</td>
      <td>Campo Essencial<br>Habilitado de campo 53- Aspecto Tomografia = 5 (Outro</td>
      <td>TOMO_OUT</td>
    </tr>
    <tr>
      <td>60- Data da Tomografia</td>
      <td>Data<br>DD/MM/AAAA</td>
      <td></td>
      <td>Se realizou tomografia, especificar a data do exame.</td>
      <td>Campo Essencial<br>Habilitado se campo 59- Aspecto Tomografia for igual a 1, 2, 3, 4 ou 5.</td>
      <td>DT_TOMO</td>
    </tr>
    <tr>
      <td>61-Coletou amostra?</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Foi realizado coleta de amostra para realização de teste diagnóstico?</td>
      <td>Campo Essencial</td>
      <td>AMOSTRA</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 17&lt;/page_number&gt;</footer>

---


## Page 18

<table>
  <tr>
    <td>62-Data da Coleta</td>
    <td>Date<br>DD/MM/AAAA</td>
    <td></td>
    <td>Data da coleta da amostra para realização do teste diagnóstico.</td>
    <td>Campo Essencial<br>Habilitado de campo 55-Coletou amostra? = 1.<br>Data deve ser maior ou igual a 2-Data de 1ºs sintomas e menor ou igual a data da digitação (atual).</td>
    <td>DT_COLETA</td>
  </tr>
  <tr>
    <td>63-Tipo de amostra</td>
    <td>Varchar2(30)</td>
    <td>1-Secreção de Naso-orofaringe<br>2-Lavado Broco-alveolar<br>3-Tecido post-mortem<br>4-Outra, qual?<br>5-LCR<br>9-Ignorado</td>
    <td>Tipo da amostra clínica coletada para o teste diagnóstico.</td>
    <td>Campo Essencial<br>Habilitado de campo 61-Coletou amostra? = 1.</td>
    <td>TP_AMOSTRA</td>
  </tr>
  <tr>
    <td>Tipo de amostra/Outra</td>
    <td>Varchar2(30)</td>
    <td></td>
    <td>Descrição do tipo da amostra clínica, caso diferente das listadas nas categorias do campo.</td>
    <td>Campo Essencial<br>Campo habilitado se selecionado categoria 4-Outra, qual em Tipo de amostra.</td>
    <td>OUT_AMOST</td>
  </tr>
  <tr>
    <td>64-Nº da Requisição do GAL</td>
    <td></td>
    <td></td>
    <td>Número da requisição de exames gerado pelo sistema GAL.</td>
    <td>Campo Essencial</td>
    <td>REQUI_GAL</td>
  </tr>
  <tr>
    <td>65- Tipo do Teste antigênico</td>
    <td>Number(3)</td>
    <td>1-Imunofluorescência (IF)<br>2- Teste rápido antigênico</td>
    <td>Tipo do teste antigênico que foi realizado.</td>
    <td>Campo Essencial</td>
    <td>TP_TES_AN</td>
  </tr>
  <tr>
    <td>66- Data do resultado teste Antigênico</td>
    <td>Data<br>DD/MM/AAAA</td>
    <td></td>
    <td>Data do resultado do teste antigênico.</td>
    <td>Campo Essencial<br>Data deve ser maior ou igual a 62- Data da Coleta</td>
    <td>DT_RES_AN</td>
  </tr>
  <tr>
    <td>67- Resultado do Teste Antigênico</td>
    <td>Varchar2(1)</td>
    <td>1-positivo<br>2-Negativo<br>3- Inconclusivo<br>4-Não realizado<br>5-Aguardando resultado<br>9-Ignorado</td>
    <td>Resultado do Teste Antigênico</td>
    <td>Campo Essencial<br>Este campo virá marcado com 5-Aguardando Resultado e estará habilitado se o campo 61-Coletou amostra? = 1</td>
    <td>RES_AN</td>
  </tr>
  <tr>
    <td>68-Laboratório que realizou o Teste antigênico</td>
    <td>Varchar2(70)</td>
    <td>Nomes dos Laboratórios cadastrados no sistema</td>
    <td>Laboratório responsável pela liberação do resultado do teste</td>
    <td>Campo Essencial<br>Habilitado se campo 67- Resultado do teste antigênico: estiver selecionado como 1-Positivo, 2- Negativo, 3- Inconclusivo ou 5- Aguardando resultado.</td>
    <td>LAB_AN</td>
  </tr>
</table>

SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 18&lt;/page_number&gt;

---


## Page 19

<table>
  <thead>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>68-Laboratório que realizou o Teste antigênico</td>
      <td>Varchar2(7)</td>
      <td>Tabela com códigos CNES</td>
      <td>antigênico.</td>
      <td>Preenchendo o nome do Laboratório, o código é preenchido automaticamente, ou vice-versa.</td>
      <td>CO_LAB_AN</td>
    </tr>
    <tr>
      <td>69-Agente etiológico – Teste Antigênico. Positivo para Influenza?</td>
      <td>Varchar2(1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Resultado do Teste Antigênico que foi positivo para Influenza</td>
      <td>Campo Essencial</td>
      <td>POS_AN_FLU</td>
    </tr>
    <tr>
      <td>69-Agente etiológico – Teste Antigênico. Se sim, qual Influenza?</td>
      <td>Varchar2(1)</td>
      <td>1-Influenza A<br>2-Influenza B</td>
      <td>Resultado do Teste Antigênico, para o tipo de Influenza.</td>
      <td>Campo Essencial<br>Habilitado se campo 69-Agente etiológico – Teste Antigênico: Positivo para Influenza? = 1.</td>
      <td>TP_FLU_AN</td>
    </tr>
    <tr>
      <td>69-Agente etiológico – Teste Antigênico. Positivo para outros vírus?</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Resultado do Teste Antigênico, que foi positivo para outro vírus respiratório.</td>
      <td>Campo Essencial</td>
      <td>POS_AN_OUT</td>
    </tr>
    <tr>
      <td>69-Agente etiológico – Teste Antigênico. SARS-CoV-2</td>
      <td>Varchar2(1)</td>
      <td>1-marcado pelo usuário<br>Vazio - não marcado</td>
      <td>Resultado do Teste Antigênico, para SARS-CoV-2.</td>
      <td>Campo Essencial<br>Habilitado se campo 69-Agente etiológico, Teste Antigênico. Positivo para outros vírus? = 1.</td>
      <td>AN_SARS2</td>
    </tr>
    <tr>
      <td>69-Agente etiológico – Teste Antigênico. VSR</td>
      <td>Varchar2(1)</td>
      <td>1-marcado pelo usuário<br>Vazio - não marcado</td>
      <td>Resultado do Teste Antigênico, para VSR.</td>
      <td>Campo Essencial<br>Habilitado se campo 69-Agente etiológico, Teste Antigênico. Positivo para outros vírus? = 1.</td>
      <td>AN_VSR</td>
    </tr>
    <tr>
      <td>69-Agente etiológico – Teste Antigênico. Parainfluenza 1</td>
      <td>Varchar2 (1)</td>
      <td>1-marcado pelo usuário<br>Vazio - não marcado</td>
      <td>Resultado do Teste Antigênico, para Parainfluenza 1.</td>
      <td>Campo Essencial<br>Habilitado se campo 69-Agente etiológico, Teste Antigênico. Positivo para outros vírus? = 1.</td>
      <td>AN_PARA1</td>
    </tr>
    <tr>
      <td>69-Agente etiológico – Teste Antigênico. Parainfluenza 2</td>
      <td>Varchar2 (1)</td>
      <td>1-marcado pelo usuário<br>Vazio - não marcado</td>
      <td>Resultado do Teste Antigênico. Parainfluenza 2.</td>
      <td>Campo Essencial<br>Habilitado se campo 69-Agente etiológico, Teste Antigênico Positivo para outros vírus? = 1.</td>
      <td>AN_PARA2</td>
    </tr>
    <tr>
      <td>69-Agente etiológico – Teste Antigênico. Parainfluenza 3</td>
      <td>Varchar2(1)</td>
      <td>1-marcado pelo usuário<br>Vazio - não marcado</td>
      <td>Resultado do Teste Antigênico. Parainfluenza 3.</td>
      <td>Campo Essencial<br>Habilitado se campo 69-Agente etiológico, Teste Antigênico. Positivo para outros vírus? = 1.</td>
      <td>AN_PARA3</td>
    </tr>
    <tr>
      <td>69-Agente etiológico – Teste Antigênico. Adenovírus</td>
      <td>Varchar2(1)</td>
      <td>1-marcado pelo usuário<br>Vazio - não marcado</td>
      <td>Resultado do Teste Antigênico. Adenovírus.</td>
      <td>Campo Essencial<br>Habilitado se campo 69-Agente etiológico, Teste Antigênico.</td>
      <td>AN_ADENO</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 19&lt;/page_number&gt;</footer>

---


## Page 20

<table>
  <thead>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>69- Agente etiológico – Teste Antigênico.<br>Outro vírus respiratório</td>
      <td>Varchar2 (1)</td>
      <td>1-marcado pelo usuário<br>Vazio - não marcado</td>
      <td>Resultado do Teste Antigênico.<br>Outro vírus respiratório.</td>
      <td>Positivo para outros vírus? = 1.<br><br>Campo Essencial<br><br>Habilitado se campo 69-Agente etiológico, Teste Antigênico.<br>Positivo para outros vírus? = 1.</td>
      <td>AN_OUTRO</td>
    </tr>
    <tr>
      <td>69- Agente etiológico – Teste Antigênico.<br>Outro vírus respiratório (Descrição)</td>
      <td>Varchar2(30)</td>
      <td></td>
      <td>Nome do outro vírus respiratório identificado pelo Teste Antigênico.</td>
      <td>Campo Essencial<br><br>Habilitado se campo 69-Agente etiológico, Teste Antigênico.<br>Positivo para outros vírus? = 1.</td>
      <td>DS_AN_OUT</td>
    </tr>
    <tr>
      <td>70-Resultado da RT-PCR/outro método por Biologia Molecular</td>
      <td>Varchar2 (1)</td>
      <td>1-Detectável<br>2-Não Detectável<br>3-Inconclusivo<br>4-Não Realizado<br>5-Aguardando Resultado<br>9-Ignorado</td>
      <td>Resultado do teste de RT-PCR/outro método por Biologia Molecular.</td>
      <td>Campo Essencial<br><br>Este campo virá marcado com 5-Aguardando Resultado e estará habilitado se o campo 61-Coletou amostra? = 1.</td>
      <td>PCR_RESUL</td>
    </tr>
    <tr>
      <td>71-Data do Resultado RT-PCR/outro método por Biologia Molecular</td>
      <td>Date<br>DD/MM/AAAA</td>
      <td></td>
      <td>Data do Resultado RT-PCR/outro método por Biologia Molecular</td>
      <td>Campo Essencial<br><br>Campo habilitado se selecionado categoria 1-Detectável, 2-Não Detectável ou 3-Inconclusivo em Resultado da RT-PCR/outro método por Biologia Molecular.<br><br>Data deve ser >= a data da coleta- campo 62.</td>
      <td>DT_PCR</td>
    </tr>
    <tr>
      <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular: Positivo para Influenza?</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Resultado da RT-PCR foi positivo para Influenza</td>
      <td>Campo Essencial</td>
      <td>POS_PCRFLU</td>
    </tr>
    <tr>
      <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular: Se sim, qual Influenza?</td>
      <td>Varchar2(1)</td>
      <td>1-Influenza A<br>2-Influenza B</td>
      <td>Resultado diagnóstico do RT-PCR para o tipo de Influenza.</td>
      <td>Campo Essencial<br><br>Habilitado se campo 72-Agente etiológico – RT_PCR/outro método por Biologia Molecular: Positivo para Influenza? = 1.</td>
      <td>TP_FLU_PCR</td>
    </tr>
    <tr>
      <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular: Se Influenza A, qual subtipo?</td>
      <td>Varchar2(1)</td>
      <td>1-Influenza A(H1N1)pdm09<br>2-Influenza A (H3N2)<br>3-Influenza A não subtipado<br>4-Influenza A não subtipável<br>5-Inconclusivo<br>6-Outro, especifique:</td>
      <td>Subtipo para Influenza A.</td>
      <td>Campo Essencial<br><br>Habilitado se campo 72-Agente etiológico – RT_PCR/outro método por Biologia Molecular: Se sim, qual Influenza? = 1.</td>
      <td>PCR_FLUASU</td>
    </tr>
    <tr>
      <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular: Se Influenza A, qual subtipo? Outro,</td>
      <td>Varchar2 (30)</td>
      <td></td>
      <td>Outro subtipo para Influenza A.</td>
      <td>Campo Essencial<br><br>Habilitado se campo 72-Agente etiológico – RT-PCR/outro método por</td>
      <td>FLUASU_OUT</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 20&lt;/page_number&gt;</footer>

---


## Page 21

<table>
  <thead>
    <tr>
      <td>especifique:</td>
      <td></td>
      <td></td>
      <td></td>
      <td>Biologia Molecular:<br>Se Influenza A, qual subtipo? = 6.</td>
      <td></td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Se Influenza B, qual linhagem?</td>
      <td>Varchar2(1)</td>
      <td>1-Victoria<br>2-Yamagatha<br>3-Não realizado<br>4-Inconclusivo<br>5-Outro, especifique:</td>
      <td>Linhagem para Influenza B.</td>
      <td>Campo Essencial<br><br>Habilitado se campo 72-Agente etiológico – RT_PCR/outro método por Biologia Molecular: Se sim, qual Influenza? = 2.</td>
      <td>PCR_FLUBLI</td>
    </tr>
    <tr>
      <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Se Influenza B, qual linhagem? Outro, especifique:</td>
      <td>Varchar2 (30)</td>
      <td></td>
      <td>Outra linhagem para Influenza B.</td>
      <td>Campo Essencial<br><br>Habilitado se 72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Se Influenza B, qual linhagem? = 5.</td>
      <td>FLUBLI_OUT</td>
    </tr>
    <tr>
      <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Positivo para outros vírus?</td>
      <td>Varchar2 (1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Resultado da RT-PCR foi positivo para outro vírus respiratório</td>
      <td>Campo Essencial</td>
      <td>POS_PCROUT</td>
    </tr>
    <tr>
      <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>SARS-CoV-2</td>
      <td>Varchar2 (1)</td>
      <td>1-marcado pelo usuário<br>Vazio - não marcado</td>
      <td>Resultado diagnóstico do RT-PCR para (SARS-CoV-2).</td>
      <td>Campo Essencial<br><br>Habilitado se campo 72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Positivo para outros vírus? = 1.</td>
      <td>PCR_SARS2</td>
    </tr>
    <tr>
      <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>VSR</td>
      <td>Varchar2 (1)</td>
      <td>1-marcado pelo usuário<br>Vazio - não marcado</td>
      <td>Resultado diagnóstico do RT-PCR para (VSR).</td>
      <td>Campo Essencial<br><br>Habilitado se campo 72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Positivo para outros vírus? = 1</td>
      <td>PCR_VSR</td>
    </tr>
    <tr>
      <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Parainfluenza 1</td>
      <td>Varchar2 (1)</td>
      <td>1-marcado pelo usuário<br>Vazio - não marcado</td>
      <td>Resultado diagnóstico do RT-PCR para Parainfluenza 1.</td>
      <td>Campo Essencial<br><br>Habilitado se campo 72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Positivo para outros vírus? = 1</td>
      <td>PCR_PARA1</td>
    </tr>
    <tr>
      <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Parainfluenza 2</td>
      <td>Varchar2 (1)</td>
      <td>1-marcado pelo usuário<br>Vazio - não marcado</td>
      <td>Resultado diagnóstico do RT-PCR para Parainfluenza 2.</td>
      <td>Campo Essencial<br><br>Habilitado se campo 72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Positivo para outros vírus? = 1</td>
      <td>PCR_PARA2</td>
    </tr>
    <tr>
      <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Parainfluenza 3</td>
      <td>Varchar2 (1)</td>
      <td>1-marcado pelo usuário<br>Vazio - não marcado</td>
      <td>Resultado diagnóstico do RT-PCR para</td>
      <td>Campo Essencial<br><br>Habilitado se campo 72- Agente etiológico – RT-PCR/outro método por</td>
      <td>PCR_PARA3</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 21&lt;/page_number&gt;</footer>

---


## Page 22

<table>
  <tr>
    <td></td>
    <td></td>
    <td></td>
    <td>Parainfluenza 3.</td>
    <td>Biologia Molecular:<br>Positivo para outros vírus? = 1</td>
    <td></td>
  </tr>
  <tr>
    <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Parainfluenza 4</td>
    <td>Varchar2 (1)</td>
    <td>1-marcado pelo usuário<br>Vazio - não marcado</td>
    <td>Resultado diagnóstico do RT-PCR para Parainfluenza 4.</td>
    <td>Campo Essencial<br>Habilitado se campo 72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Positivo para outros vírus? = 1</td>
    <td>PCR_PARA4</td>
  </tr>
  <tr>
    <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Adenovírus</td>
    <td>Varchar2 (1)</td>
    <td>1-marcado pelo usuário<br>Vazio - não marcado</td>
    <td>Resultado diagnóstico do RT-PCR para Adenovírus.</td>
    <td>Campo Essencial<br>Habilitado se campo 72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Positivo para outros vírus? = 1</td>
    <td>PCR_ADENO</td>
  </tr>
  <tr>
    <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Metapneumovírus</td>
    <td>Varchar2 (1)</td>
    <td>1-marcado pelo usuário<br>Vazio - não marcado</td>
    <td>Resultado diagnóstico do RT-PCR para Metapneumovírus.</td>
    <td>Campo Essencial<br>Habilitado se campo 72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Positivo para outros vírus? = 1</td>
    <td>PCR_METAP</td>
  </tr>
  <tr>
    <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Bocavírus</td>
    <td>Varchar2 (1)</td>
    <td>1-marcado pelo usuário<br>Vazio - não marcado</td>
    <td>Resultado diagnóstico do RT-PCR para Bocavírus.</td>
    <td>Campo Essencial<br>Habilitado se campo 72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Positivo para outros vírus? = 1</td>
    <td>PCR_BOCA</td>
  </tr>
  <tr>
    <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Rinovírus</td>
    <td>Varchar2 (1)</td>
    <td>1-marcado pelo usuário<br>Vazio - não marcado</td>
    <td>Resultado diagnóstico do RT-PCR para Rinovírus.</td>
    <td>Campo Essencial<br>Habilitado se campo 72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Positivo para outros vírus? = 1</td>
    <td>PCR_RINO</td>
  </tr>
  <tr>
    <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Outro vírus respiratório, especifique:</td>
    <td>Varchar2 (1)</td>
    <td>1-marcado pelo usuário<br>Vazio - não marcado</td>
    <td>Resultado diagnóstico do RT-PCR para Outro vírus respiratório.</td>
    <td>Campo Essencial<br>Habilitado se campo 72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Positivo para outros vírus? = 1</td>
    <td>PCR_OUTRO</td>
  </tr>
  <tr>
    <td>72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Outro vírus respiratório (Descrição)</td>
    <td>Varchar2 (30)</td>
    <td></td>
    <td>Nome do outro vírus respiratório identificado pelo RT-PCR.</td>
    <td>Campo Essencial<br>Habilitado se 72- Agente etiológico – RT-PCR/outro método por Biologia Molecular:<br>Outro vírus respiratório, especifique:</td>
    <td>DS_PCR_OUT</td>
  </tr>
  <tr>
    <td>73-Laboratório que realizou RT-PCR/outro método por Biologia</td>
    <td>Varchar2 (7)</td>
    <td>Tabela com códigos CNES e nomes dos Laboratórios</td>
    <td>Laboratório responsável pela</td>
    <td>Campo Essencial</td>
    <td>LAB_PCR OU CO_LAB_PCR</td>
  </tr>
</table>

SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 22&lt;/page_number&gt;

---


## Page 23

<table>
  <tr>
    <td>Molecular<br>Código (CNES)</td>
    <td></td>
    <td>cadastrados no sistema.</td>
    <td>liberação do<br>resultado do teste<br>diagnóstico (RT-<br>PCR) da amostra do<br>paciente.</td>
    <td>Habilitado se selecionado categoria 1-Detectável, 2-Não Detectável ou 3-Inconclusivo em 70-Resultado da RT-PCR/outro método por Biologia Molecular.<br>Preenchendo o nome do Laboratório, o código é preenchido automaticamente, ou vice-versa.</td>
    <td></td>
  </tr>
  <tr>
    <td>74- Tipo de Amostra Sorológica para SARS-Cov-2</td>
    <td>Number(3)</td>
    <td>1- Sangue/plasma/soro<br>2-Outra, qual?<br>9-Ignorado</td>
    <td>Tipo de amostra sorológica que foi coletada.</td>
    <td>Campo Essencial</td>
    <td>TP_AM_SOR</td>
  </tr>
  <tr>
    <td>Tipo de Amostra Sorológica para SARS-Cov-2/Outra, qual?</td>
    <td></td>
    <td></td>
    <td>Descrição do tipo da amostra clínica, caso diferente das listadas na categoria um (1) do campo.</td>
    <td>Campo Essencial<br>Campo habilitado se selecionado categoria 2-Outra, qual? em Tipo de Amostra Sorológica.</td>
    <td>SOR_OUT</td>
  </tr>
  <tr>
    <td>75- Data da coleta</td>
    <td>Data<br>DD/MM/AAAA</td>
    <td></td>
    <td>Data da coleta do material para diagnóstico por Sorologia.</td>
    <td>Campo Essencial<br>Habilitado de campo 61-Coletou amostra? = 1.<br>Data deve ser maior ou igual a 2-Data de 1ºs sintomas e menor ou igual a data da digitação (atual).</td>
    <td>DT_CO_SOR</td>
  </tr>
  <tr>
    <td>76- Tipo de Sorologia para SARS-Cov-2</td>
    <td>Number(3)</td>
    <td>1-Teste rápido<br>2-Elisa<br>3- Quimiluminescência<br>4- Outro, qual</td>
    <td>Tipo do Teste Sorológico que foi realizado</td>
    <td>Campo Essencial</td>
    <td>TP_SOR</td>
  </tr>
  <tr>
    <td>76- Tipo de Sorologia para SARS-Cov-2</td>
    <td>Varchar 2(100)</td>
    <td></td>
    <td>Descrição do tipo de Teste Sorológico</td>
    <td>Campo Essencial<br>Campo habilitado se selecionado categoria 4-Outro, qual? em Tipo de Sorologia.</td>
    <td>OUT_SOR</td>
  </tr>
  <tr>
    <td>76- Tipo de Sorologia para SARS-Cov-2/Outro, qual?</td>
    <td>Varchar 2(100)</td>
    <td></td>
    <td>Outro tipo de amostra Sorológica</td>
    <td></td>
    <td>SOR_OUT</td>
  </tr>
  <tr>
    <td>76- Resultado do Teste Sorológico para SARS-CoV-2:</td>
    <td>Varchar2(1)</td>
    <td>IgG</td>
    <td>Resultado da Sorologia para SARS-CoV-2</td>
    <td>Campo Essencial</td>
    <td>RES_IGG</td>
  </tr>
  <tr>
    <td>76- Resultado do Teste Sorológico para SARS-CoV-2:</td>
    <td>Varchar2(1)</td>
    <td>IgM</td>
    <td>Resultado da Sorologia para SARS-CoV-2</td>
    <td>Campo Essencial</td>
    <td>RES_IGM</td>
  </tr>
  <tr>
    <td>76- Resultado do Teste Sorológico para SARS-CoV-2:</td>
    <td>Varchar2(1)</td>
    <td>IgA</td>
    <td>Resultado da Sorologia para</td>
    <td>Campo Essencial</td>
    <td>RES_IGA</td>
  </tr>
</table>

SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 23&lt;/page_number&gt;

---


## Page 24

<table>
  <tr>
    <td></td>
    <td></td>
    <td></td>
    <td>SARS-CoV-2</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>77- Data do Resultado</td>
    <td>Date<br>DD/MM/AAAA</td>
    <td></td>
    <td>Data do Resultado<br>do Teste Sorológico</td>
    <td>Campo Essencial<br>Data deve ser maior ou igual a 75- Data da Coleta</td>
    <td>DT_RES</td>
  </tr>
  <tr>
    <td>78- Faz parte de uma cadeia de surto<br>de SG?</td>
    <td>Varchar2(1)</td>
    <td>1-Sim<br>2-Não<br>9-Ignorado</td>
    <td>O caso faz parte de<br>uma cadeia de<br>surto de SG.</td>
    <td>Campo essencial</td>
    <td>SURTO_SG</td>
  </tr>
  <tr>
    <td>79- É um caso de co-detecção?</td>
    <td>Varchar2(1)</td>
    <td>1-Sim<br>2-Não<br>9-Ignorado</td>
    <td>O caso trata-se de<br>co-detecção, onde<br>foram identificados<br>dois tipos de vírus<br>ao mesmo tempo.</td>
    <td>Campo essencial</td>
    <td>CO-DETEC</td>
  </tr>
  <tr>
    <td>80-Classificação final do caso</td>
    <td>Varchar2(1)</td>
    <td>1-SRAG por influenza<br>2-SRAG por outro vírus<br>respiratório<br>3-SRAG por outro agente<br>etiológico, qual:<br>4-SRAG não especificado<br>5-SRAG por covid-19</td>
    <td>Diagnóstico final do<br>caso.<br><br>Se tiver resultados<br>divergentes entre<br>as metodologias<br>laboratoriais,<br>priorizar o<br>resultado do RT-<br>PCR.</td>
    <td>Campo Obrigatório</td>
    <td>CLASSI_FIN</td>
  </tr>
  <tr>
    <td>80-Classificação final do caso<br>3-SRAG por outro agente etiológico,<br>qual:</td>
    <td>Varchar2(30)</td>
    <td></td>
    <td>Descrição de qual<br>outro agente<br>etiológico foi<br>identificado</td>
    <td>Campo Obrigatório<br><br>Se campo 80-Classificação final do caso = 3.<br><br>Habilitado se campo 80-Classificação final do caso = 3.</td>
    <td>CLASSI_OUT</td>
  </tr>
  <tr>
    <td>81-Critério de Encerramento</td>
    <td>Varchar2(1)</td>
    <td>1. Laboratorial<br>2. Clínico Epidemiológico<br>3. Clínico<br>4. Clínico Imagem</td>
    <td>Indicar qual o<br>critério de<br>confirmação.</td>
    <td>Campo Essencial<br>OBS. Os critérios de encerramento: 3. clínico e 4. clínico-imagem , não são<br>mais considerados para o encerramento de SRAG por covid-19 desde<br>31/10/2022. ATENÇÃO: O critério de encerramento clínico-imagem, não é<br>utilizado para encerramento de SRAG por Influenza, por outros vírus<br>respiratórios, por outro agente etiológico e por SRAG não especificado.</td>
    <td>CRITERIO</td>
  </tr>
  <tr>
    <td>82-Evolução do caso</td>
    <td>Varchar2(1)</td>
    <td>1-Cura<br>2-Óbito<br>3- Óbito por outras causas<br>9-Ignorado</td>
    <td>Evolução do caso</td>
    <td>Campo Essencial</td>
    <td>EVOLUCAO</td>
  </tr>
</table>

SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 24&lt;/page_number&gt;

---


## Page 25

<table>
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>83-Data da alta ou óbito</td>
      <td>Date<br>DD/MM/AAAA</td>
      <td>Data da alta ou<br>óbito</td>
      <td>Campo Essencial<br><br>Data da alta ou do óbito deve ser > ou = a data dos primeiros sintomas e <= a data da digitação (atual).<br><br>Habilitado se campo 82- Evolução do caso = 1 ou 2.</td>
      <td>DT_EVOLUCA</td>
      <td></td>
    </tr>
    <tr>
      <td>84-Data do Encerramento</td>
      <td>Date<br>DD/MM/AAAA</td>
      <td>Data do<br>encerramento do<br>caso.</td>
      <td>Campo Obrigatório<br><br>Se o campo 80- Classificação final do caso estiver preenchido.<br><br>Data do encerramento deve ser > ou = a data do preenchimento.<br><br>Data do encerramento deve ser < ou = a data da digitação (atual).</td>
      <td>DT_ENCERRA</td>
      <td></td>
    </tr>
    <tr>
      <td>85- Número D.O</td>
      <td></td>
      <td>Número da<br>Declaração de<br>Óbito</td>
      <td>Campo Essencial<br><br>Habilitado se o campo 80- Evolução do caso = 2 ou 3</td>
      <td>NU_DO</td>
      <td></td>
    </tr>
    <tr>
      <td>86-Observações</td>
      <td>Varchar2(999)</td>
      <td>Outras observações<br>sobre o paciente<br>consideradas<br>pertinentes.</td>
      <td>Campo Opcional</td>
      <td>OBSERVA</td>
      <td></td>
    </tr>
    <tr>
      <td>87-Profissional de Saúde Responsável</td>
      <td>Varchar2(60)</td>
      <td>Nome completo do<br>profissional de<br>saúde (sem<br>abreviações)<br>responsável pela<br>notificação.</td>
      <td>Campo Essencial</td>
      <td>NOME_PROF</td>
      <td></td>
    </tr>
    <tr>
      <td>88-Registro Conselho/Matrícula</td>
      <td>Varchar2(15)</td>
      <td>Número do<br>conselho ou<br>matrícula do<br>profissional de<br>saúde responsável<br>pela notificação<br>(Ex: CRM/RJ 1234)</td>
      <td>Campo Essencial</td>
      <td>REG_PROF</td>
      <td></td>
    </tr>
    <tr>
      <td>Data da digitação</td>
      <td>Date<br>DD/MM/AAAA</td>
      <td>Data de inclusão do<br>registro no sistema.</td>
      <td>Campo Interno<br><br>Preenchido automaticamente pelo sistema com a data da digitação da ficha.<br>Não é a data de preenchimento da ficha manualmente e sim a data em que<br>é digitado no sistema.<br><b>Não é atualizada se houver alterações posteriores de dados.</b></td>
      <td>DT_DIGITA</td>
      <td></td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 25&lt;/page_number&gt;</footer>

---


## Page 26

<table>
  <thead>
    <tr>
      <td>89- Designação da variante (OMS)</td>
      <td>Varchar2(1)</td>
      <td>1- Ômicron<br>2- Delta<br>3- Alfa<br>4- Beta<br>5- Gama<br>6- Recombinante (Exemplos: XE, XF, XQ, XS...)<br>7- Outra, especifique:</td>
      <td>Denominação da variante identificada de acordo com a designação da Organização Mundial da Saúde (OMS).</td>
      <td>Campo Essencial</td>
      <td>VG_OMS</td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>89- Designação da variante (OMS): Outra, especifique:</td>
      <td>Varchar2 (30)</td>
      <td></td>
      <td>Denominação de novas variantes, que ainda não constam na relação disponível.</td>
      <td>Campo Essencial</td>
      <td>VG_OMSOUT</td>
    </tr>
    <tr>
      <td>90- Linhagem da variante</td>
      <td>Varchar2 (15)</td>
      <td></td>
      <td>Especificação da linhagem identificada no resultado do sequenciamento genômico.</td>
      <td>Campo Essencial<br>Se o campo 89- Designação da variante (OMS) for preenchido, esse campo passa a ser de preenchimento obrigatório.</td>
      <td>VG_LIN</td>
    </tr>
    <tr>
      <td>91- Método laboratorial mais recente</td>
      <td>Varchar2(1)</td>
      <td>1- Sequenciamento genômico completo<br>2- Sequenciamento genômico parcial<br>3. RT-PCR em tempo real de inferência<br>4-Outro, especifique</td>
      <td>Metodologia laboratorial que foi realizada mais recente</td>
      <td>Campo Essencial</td>
      <td>VG_MET</td>
    </tr>
    <tr>
      <td>91- Método laboratorial mais recente: Outro, especifique</td>
      <td>Varchar2 (30)</td>
      <td></td>
      <td></td>
      <td>Habilitado se campo 91- Método laboratorial mais recente = 4.</td>
      <td>VG_METOUT</td>
    </tr>
    <tr>
      <td>92- Nome do laboratório</td>
      <td>Varchar2(70)</td>
      <td></td>
      <td>Laboratório responsável pela liberação do resultado do sequenciamento da amostra do paciente.</td>
      <td>Campo Essencial</td>
      <td>VG_LAB</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 26&lt;/page_number&gt;</footer>

---


## Page 27

<table>
  <thead>
    <tr>
      <td>93- Código (CNES) do laboratório</td>
      <td>Varchar2 (7)</td>
      <td>Código Cadastro Nacional de Estabelecimento de Saúde (CNES).</td>
      <td>Campo Essencial</td>
      <td>VG_CODLAB</td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>94- Data do resultado</td>
      <td>Date DD/MM/AAAA</td>
      <td></td>
      <td>Campo Essencial</td>
      <td>VG_DTRES</td>
    </tr>
    <tr>
      <td>95- Encerramento do caso (para VOC, VOI ou VUM)</td>
      <td>Varchar2(1)</td>
      <td>1- Confirmado por Sequenciamento genômico completo<br>2- Provável por Sequenciamento genômico parcial)<br>3- Sugestivo por RT-PCR de inferência<br>4- Sugestivo por vínculo epidemiológico<br>5- Descartado</td>
      <td>Encerramento do caso conforme orientações na Nota Técnica (NT) 1.129/2021-CGPNI/DEIDT/SVS/MS.</td>
      <td>Campo Essencial<br>Se o campo 89- Designação da variante (OMS) for preenchido, esse campo passa a ser de preenchimento obrigatório.</td>
      <td>VG_ENC</td>
    </tr>
    <tr>
      <td>96- Possível caso de reinfecção por covid-19?</td>
      <td>Varchar2(1)</td>
      <td>1-Sim<br>2-Não<br>9-Ignorado</td>
      <td>Possível caso de reinfecção (paciente com registro anterior positivo para covid-19, com intervalo maior ou igual a 90 dias).</td>
      <td>Campo Essencial</td>
      <td>VG_REINF</td>
    </tr>
    <tr>
      <td>97- Profissional responsável pelo preenchimento</td>
      <td>Varchar2 (60)</td>
      <td></td>
      <td>Nome completo do profissional de saúde (sem abreviações) responsável pelo preenchimento das informações de Vigilância Genômica Epidemiológica e Reinfecção.</td>
      <td>Campo Essencial</td>
      <td>VG_PROF</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 27&lt;/page_number&gt;</footer>

---


## Page 28

<table>
  <thead>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>98- Estabelecimento responsável pelo preenchimento</td>
      <td>Varchar2 (60)</td>
      <td>Estabelecimento responsável pelo preenchimento da informação.</td>
      <td>Campo Essencial<br>Se o campo 89- Designação da variante (OMS) for preenchido, esse campo passa a ser de preenchimento obrigatório.</td>
      <td>VG_EST</td>
    </tr>
    <tr>
      <td>98- Código (CNES) do Estabelecimento responsável pelo preenchimento</td>
      <td>Varchar2 (7)</td>
      <td>Código Cadastro Nacional de Estabelecimento de Saúde (CNES).</td>
      <td>Campo Essencial</td>
      <td>VG_CODDEST</td>
    </tr>
  </tbody>
</table>

<footer>SIVEP Gripe- Sistema de Informação da Vigilância Epidemiológica da Gripe. &lt;page_number&gt;Página 28&lt;/page_number&gt;</footer>