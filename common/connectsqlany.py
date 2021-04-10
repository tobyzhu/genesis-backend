
import sqlanydb


def connectdb(server):
    if server == 'sqlany':
        read = sqlanydb.connect(link="tcpip(host=localhost)",
                                ServerName='hdms',
                                uid='sa',
                                pwd='iHaVeFuN',
                                dbn='hdms')


    return read


def disconnectdb(read):
    read.close()

    return 0


def ReadEmpl():

    read = connectdb('sqlany')
    Rcursor = read.cursor()

    # 商品基本信息
    readsql =   " select ecode, ename " \
                " from empl  "
    Rcursor.execute(readsql)
    readResult = Rcursor.fetchall()

    print(readResult)

ReadEmpl()